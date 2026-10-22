# File & Image Storage (S3)

## What is needed

Profile pictures and CIO-uploaded images need to persist reliably. Heroku's filesystem is ephemeral — anything written outside the database disappears on every redeploy — so local disk storage isn't an option in production, and storing binary files in PostgreSQL isn't either.

## Plan

`django-storages` with its S3 backend will be wired in through `DEFAULT_FILE_STORAGE`, conditionally: if AWS credentials are present in the environment, Django will route all `ImageField`/`FileField` uploads to S3; if they're absent (local development without S3 configured), it will fall back to the filesystem under `MEDIA_ROOT`. This means the same model code (`profile_picture = models.ImageField(...)`) will work identically in both environments without any S3-specific logic in the views or templates — `.url` will just resolve to whichever backend is active.

Settings will be tuned for signed, non-public access: `AWS_QUERYSTRING_AUTH` on with a one-hour expiry, and `AWS_S3_FILE_OVERWRITE` off so two users uploading files with the same name don't clobber each other.

This will cover both uploaded images called out in the base feature set — user profile pictures and CIO gallery photos — through the same storage path.
