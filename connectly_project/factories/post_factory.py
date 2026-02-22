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
        # If content is provided, use that; if not, use title as the post content
        post_content = content if content not in (None, "") else (title or "")

        # Create the post but don't save yet so the view can add author first
        # Author is required sa Post model kaya need nating mag-assign bago ma-save
        return Post(content=post_content)