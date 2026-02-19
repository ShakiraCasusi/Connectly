from posts.models import Post


class PostFactory:
    """
    Factory used by the Posts API to centralize validation/creation.

    Note: The current Post model in this project is a simple text post:
      - content
      - author
      - created_at

    Some earlier iterations of this project referenced post_type/metadata/title.
    To maintain backward compatibility with existing view code and docs, this
    factory accepts those arguments but gracefully falls back to creating a
    basic text post instance (unsaved) when those fields do not exist.
    """

    @staticmethod
    def create_post(post_type=None, title="", content="", metadata=None):
        # Prefer "content" if explicitly passed; otherwise treat "title" as the content.
        post_content = content if content not in (None, "") else (title or "")

        # Create an UNSAVED instance so the view can attach author before saving.
        # (author is a required FK in the current schema)
        return Post(content=post_content)