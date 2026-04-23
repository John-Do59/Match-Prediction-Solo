"""
Email service — utilise l'API Resend pour l'envoi transactionnel.

Configuration requise dans .env :
    RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxx
    FRONTEND_URL=http://localhost:8082    # utilisé pour les liens dans les emails

En développement sans clé Resend, les emails sont loggés dans la console.
"""
import logging
import os

logger = logging.getLogger(__name__)


def _get_resend_client():
    """Retourne le client Resend si la clé API est configurée, sinon None."""
    api_key = os.getenv("RESEND_API_KEY", "")
    if not api_key or api_key.startswith("re_PLACEHOLDER"):
        return None
    try:
        import resend
        resend.api_key = api_key
        return resend
    except ImportError:
        logger.warning("Librairie 'resend' non installée. Installez-la avec: pip install resend")
        return None


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Envoie un email de réinitialisation de mot de passe.

    En développement (RESEND_API_KEY absent), affiche le lien dans les logs.
    En production, envoie via l'API Resend.

    Returns:
        True si l'email a été envoyé (ou simulé en dev), False en cas d'erreur.
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8082")
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
    from_email = os.getenv("EMAIL_FROM", "noreply@match-prediction.app")

    resend_client = _get_resend_client()

    if resend_client is None:
        # Mode développement : log sécurisé (pas de print en clair)
        logger.info(
            "DEV MODE — Password reset link for %s: %s",
            to_email,
            reset_link,
        )
        return True

    try:
        resend_client.Emails.send({
            "from": from_email,
            "to": [to_email],
            "subject": "Réinitialisation de votre mot de passe — Match Prediction",
            "html": f"""
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Réinitialisation de mot de passe</h2>
                <p>Vous avez demandé à réinitialiser votre mot de passe.</p>
                <p>Cliquez sur le bouton ci-dessous dans les <strong>15 minutes</strong> :</p>
                <a href="{reset_link}"
                   style="display:inline-block; padding:12px 24px; background:#4F46E5;
                          color:#fff; text-decoration:none; border-radius:6px;">
                    Réinitialiser mon mot de passe
                </a>
                <p style="margin-top:16px; color:#6B7280; font-size:0.875rem;">
                    Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
                    Votre mot de passe ne sera pas modifié.
                </p>
            </div>
            """,
        })
        logger.info("Password reset email sent to %s", to_email)
        return True

    except Exception as exc:
        logger.error("Failed to send password reset email to %s: %s", to_email, exc)
        return False
