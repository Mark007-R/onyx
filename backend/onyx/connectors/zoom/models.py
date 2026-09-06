from pydantic import BaseModel, Field


class ZoomTranscript(BaseModel):
    """Response shape of `GET /meetings/{meetingId}/transcript`."""

    meeting_id: str | None = None
    meeting_topic: str | None = None
    host_id: str | None = None
    can_download: bool | None = None
    download_url: str | None = None
    download_restriction_reason: str | None = None
    transcript_created_time: str | None = None
    auto_delete: bool | None = None
    auto_delete_date: str | None = None

    @property
    def is_downloadable(self) -> bool:
        """Zoom documents these three fields as mutually exclusive, then their
        own example returns all three together, so no one of them can be trusted.
        """
        return (
            self.can_download is not False
            and self.download_restriction_reason is None
            and bool(self.download_url)
        )


class ZoomSessionDetails(BaseModel):
    """The fields the connector reads from `GET /past_meetings/{meetingId}` and
    from `GET /webinars/{webinarId}`, which return much more than this."""

    uuid: str | None = None
    topic: str | None = None
    start_time: str | None = None
    duration: int | None = None


class ZoomSessionOccurrence(BaseModel):
    """One entry from `GET /past_meetings/{meetingId}/instances` or
    `GET /past_webinars/{webinarId}/instances` — identical shapes under
    different response keys."""

    uuid: str
    start_time: str | None = None


class ZoomUser(BaseModel):
    """The fields the connector reads from `GET /users` and from
    `GET /groups/{groupId}/members` — two endpoints that describe a user the
    same way under different response keys."""

    id: str | None = None
    email: str | None = None


class ZoomUserPage(BaseModel):
    users: list[ZoomUser] = Field(default_factory=list)
    next_page_token: str | None = None


class ZoomRecordingEntry(BaseModel):
    """One entry from the `meetings` array of `GET /users/{userId}/recordings`."""

    uuid: str
    # Zoom sends the meeting number as an integer here and as a string everywhere else.
    id: int | str | None = None
    topic: str | None = None
    start_time: str | None = None
    type: int | str | None = None

    @property
    def session_id(self) -> str:
        # A recording uploaded through the web portal has no meeting number.
        return str(self.id) if self.id is not None else self.uuid


class ZoomRecordingPage(BaseModel):
    recordings: list[ZoomRecordingEntry] = Field(default_factory=list)
    next_page_token: str | None = None


class ZoomParticipant(BaseModel):
    """One entry from `GET /past_meetings/{meetingId}/participants` or
    `GET /past_webinars/{webinarId}/participants`."""

    # Zoom blanks this for anyone outside the host's account, so it is not
    # required and callers must cope with an empty string.
    user_email: str | None = None
    name: str | None = None


# Zoom has no cancelled state: cancelling a registration sets the status to
# "denied". The other values are "approved" and "pending".
APPROVED_REGISTRANT_STATUS = "approved"

# Zoom's own error codes, which it sends in the response body under an HTTP 400
# or 404. NOT_ENTITLED really is "200" — it is a Zoom code, not an HTTP status.
# Compare them as text: Zoom sends the code as a number on some endpoints and as
# a string on others.
ZOOM_MEETING_TOO_OLD_CODE = "12702"
ZOOM_NOT_FOUND_CODE = "3001"
ZOOM_NOT_ENTITLED_CODE = "200"


class ZoomRegistrant(BaseModel):
    """One entry from `GET /meetings/{meetingId}/registrants` or
    `GET /webinars/{webinarId}/registrants`."""

    email: str | None = None
    status: str | None = None


class ZoomInvitee(BaseModel):
    """One entry of `settings.meeting_invitees[]` from
    `GET /meetings/{meetingId}`. Webinars have no equivalent field."""

    email: str | None = None
    internal_user: bool = False


class ZoomPanelist(BaseModel):
    """One entry from `GET /webinars/{webinarId}/panelists` — a webinar
    speaker, who does not necessarily register or appear as a participant."""

    email: str | None = None
    name: str | None = None
