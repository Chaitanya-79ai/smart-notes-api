from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import create_access_token, get_current_user, hash_password, verify_password
from app.database import Base, engine, get_db


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notes App API",
    description="Backend APIs for a multi-user notes app assignment.",
    version="1.0.0",
)


ACTION_KEYWORDS = [
    "need to",
    "should",
    "must",
    "todo",
    "finish",
    "submit",
    "deploy",
    "email",
    "call",
    "revise",
    "fix",
    "check",
    "prepare",
    "update",
    "implement",
    "test",
    "review",
    "push",
    "clean up",
]


def extract_action_items(text: str) -> list[str]:
    sentences = text.replace("!", ".").replace("?", ".").split(".")
    action_items = []
    seen_items = set()

    for sentence in sentences:
        cleaned_sentence = " ".join(sentence.strip().split())

        if not cleaned_sentence:
            continue

        lower_sentence = cleaned_sentence.lower()
        has_action_keyword = any(keyword in lower_sentence for keyword in ACTION_KEYWORDS)

        if not has_action_keyword:
            continue

        action_item = cleaned_sentence

        cleanup_prefixes = [
            "tomorrow i need to ",
            "today i need to ",
            "before submitting the form, i should ",
            "before submitting, i should ",
            "i need to ",
            "we need to ",
            "need to ",
            "i should ",
            "we should ",
            "should ",
            "i must ",
            "we must ",
            "must ",
        ]

        lower_action_item = action_item.lower()
        for prefix in cleanup_prefixes:
            if lower_action_item.startswith(prefix):
                action_item = action_item[len(prefix):].strip()
                break

        normalized_item = action_item.lower()
        if normalized_item not in seen_items:
            action_items.append(action_item)
            seen_items.add(normalized_item)

    return action_items


def get_readable_note(note_id: int, current_user: models.User, db: Session):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    is_owner = note.owner_id == current_user.id
    is_shared = (
        db.query(models.SharedNote)
        .filter(
            models.SharedNote.note_id == note_id,
            models.SharedNote.shared_with_user_id == current_user.id,
        )
        .first()
        is not None
    )

    if not is_owner and not is_shared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    return note


@app.get("/")
def health_check():
    return {"message": "Notes API is running"}


@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.MessageResponse)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = models.User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@app.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "Invalid email or password"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token}


@app.post("/notes", status_code=status.HTTP_201_CREATED, response_model=schemas.NoteResponse)
def create_note(
    note_data: schemas.NoteCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_note = models.Note(
        title=note_data.title,
        content=note_data.content,
        owner_id=current_user.id,
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


@app.get("/notes", response_model=list[schemas.NoteResponse])
def get_notes(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notes = db.query(models.Note).filter(models.Note.owner_id == current_user.id).all()
    return notes


@app.get("/notes/{note_id}", response_model=schemas.NoteResponse)
def get_note(
    note_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_readable_note(note_id, current_user, db)


@app.put("/notes/{note_id}", response_model=schemas.NoteResponse)
def update_note(
    note_id: int,
    note_data: schemas.NoteUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.owner_id == current_user.id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    note.title = note_data.title
    note.content = note_data.content

    db.commit()
    db.refresh(note)

    return note


@app.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.owner_id == current_user.id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    db.delete(note)
    db.commit()

    return None


@app.post("/notes/{note_id}/share", response_model=schemas.MessageResponse)
def share_note(
    note_id: int,
    share_data: schemas.ShareNoteRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = (
        db.query(models.Note)
        .filter(models.Note.id == note_id, models.Note.owner_id == current_user.id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    target_user = db.query(models.User).filter(models.User.email == share_data.share_with_email).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User to share with not found",
        )

    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot share a note with yourself",
        )

    existing_share = (
        db.query(models.SharedNote)
        .filter(
            models.SharedNote.note_id == note_id,
            models.SharedNote.shared_with_user_id == target_user.id,
        )
        .first()
    )

    if existing_share:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note already shared with this user",
        )

    shared_note = models.SharedNote(
        note_id=note_id,
        shared_with_user_id=target_user.id,
    )

    db.add(shared_note)
    db.commit()

    return {"message": "Note shared successfully"}


@app.get("/search", response_model=list[schemas.NoteResponse])
def search_notes(
    q: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    search_term = f"%{q}%"

    notes = (
        db.query(models.Note)
        .filter(
            models.Note.owner_id == current_user.id,
            (models.Note.title.ilike(search_term)) | (models.Note.content.ilike(search_term)),
        )
        .all()
    )

    return notes


@app.get("/notes/{note_id}/actions", response_model=schemas.ActionItemsResponse)
def get_note_actions(
    note_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = get_readable_note(note_id, current_user, db)
    action_items = extract_action_items(note.content)

    return {
        "note_id": note.id,
        "action_items": action_items,
    }


@app.get("/about")
def about():
    return {
        "name": "Chaitanya",
        "email": "ch.chaitanya79@gmail.com",
        "my features": {
            "Smart Action Item Extraction": "Added GET /notes/{id}/actions to extract possible tasks from a note using lightweight NLP-style rules. I chose this because notes often contain hidden todos, and turning them into action items makes the app more useful and productivity-focused.",
            "Search notes": "Added GET /search?q=keyword so users can quickly find notes by title or content."
        },
    }