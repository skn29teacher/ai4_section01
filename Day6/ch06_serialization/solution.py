from pydantic import BaseModel


class Profile(BaseModel):
    nickname: str
    bio: str | None = None
    active: bool = True


class ProfilePatch(BaseModel):
    nickname: str | None = None
    bio: str | None = None
    active: bool | None = None


def main() -> None:
    stored = Profile(nickname='old', bio='소개 글', active=True)
    patch = ProfilePatch(nickname='new')
    changes = patch.model_dump(exclude_unset=True)
    updated = Profile.model_validate({**stored.model_dump(), **changes})
    print('수정된 모델:', updated.model_dump())
    print('explicit null:', ProfilePatch(bio=None).model_dump(exclude_unset=True))
    print('unset:', ProfilePatch().model_dump(exclude_unset=True))
    print('06장 정답 실행 성공')


if __name__ == '__main__':
    main()
