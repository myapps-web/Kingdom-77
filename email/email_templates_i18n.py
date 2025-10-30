"""
Email Templates Localization for Kingdom-77 Bot
================================================
Contains all email templates in 5 languages: EN, AR, ES, FR, DE
"""

from typing import Dict, Any

# Email templates for all supported languages
EMAIL_TEMPLATES = {
    # ========== ENGLISH (EN) ==========
    "en": {
        "subscription_confirmation": {
            "subject": "✅ Welcome to Kingdom-77 Premium!",
            "greeting": "Hi {user_name}!",
            "title": "Welcome to Premium!",
            "message": "Thank you for subscribing to Kingdom-77 Premium for <strong>{guild_name}</strong>.",
            "details": "Subscription Details:",
            "tier": "Tier",
            "amount": "Amount",
            "interval": "Billing",
            "next_billing": "Next Billing Date",
            "features_title": "Your Premium Features:",
            "features": [
                "2x XP Boost for all members",
                "Custom embed colors",
                "Priority support",
                "Advanced statistics",
                "Custom commands"
            ],
            "cta": "Go to Dashboard",
            "footer": "If you have any questions, contact our support team.",
            "unsubscribe": "Unsubscribe from emails"
        },
        "subscription_renewal": {
            "subject": "✅ Kingdom-77 Premium Renewed",
            "greeting": "Hi {user_name}!",
            "title": "Subscription Renewed",
            "message": "Your Premium subscription for <strong>{guild_name}</strong> has been successfully renewed.",
            "amount_charged": "Amount Charged: ${amount}",
            "next_billing": "Next Billing: {next_billing_date}",
            "cta": "View Subscription",
            "footer": "Thank you for your continued support!"
        },
        "subscription_cancelled": {
            "subject": "❌ Kingdom-77 Premium Cancelled",
            "greeting": "Hi {user_name}!",
            "title": "Subscription Cancelled",
            "message": "Your Premium subscription for <strong>{guild_name}</strong> has been cancelled.",
            "expires_on": "Your Premium features will remain active until: <strong>{expiry_date}</strong>",
            "feedback": "We'd love to hear why you cancelled. Your feedback helps us improve.",
            "cta": "Reactivate Premium",
            "footer": "We hope to see you back soon!"
        },
        "subscription_expired": {
            "subject": "⏰ Kingdom-77 Premium Expired",
            "greeting": "Hi {user_name}!",
            "title": "Premium Expired",
            "message": "Your Premium subscription for <strong>{guild_name}</strong> has expired.",
            "renew_message": "Want to continue enjoying Premium features?",
            "cta": "Renew Now",
            "footer": "Get 10% off if you renew within 7 days!"
        },
        "payment_failed": {
            "subject": "⚠️ Payment Failed - Action Required",
            "greeting": "Hi {user_name}!",
            "title": "Payment Failed",
            "message": "We couldn't process your payment for <strong>{guild_name}</strong> Premium subscription.",
            "reason": "Reason: {failure_reason}",
            "action_required": "Please update your payment method to avoid service interruption.",
            "expiry_warning": "Your subscription will expire on <strong>{expiry_date}</strong> if payment is not received.",
            "cta": "Update Payment Method",
            "footer": "Need help? Contact our support team."
        },
        "trial_started": {
            "subject": "🎉 Your 7-Day Premium Trial Has Started!",
            "greeting": "Hi {user_name}!",
            "title": "Trial Started!",
            "message": "Welcome to your 7-day free trial of Kingdom-77 Premium for <strong>{guild_name}</strong>!",
            "trial_ends": "Trial Ends: {trial_end_date}",
            "features_title": "Enjoy these Premium features:",
            "features": [
                "2x XP Boost",
                "Custom colors",
                "Priority support",
                "Advanced stats",
                "Custom commands"
            ],
            "auto_renewal": "Your trial will automatically convert to a paid subscription unless cancelled.",
            "cta": "Explore Features",
            "footer": "No charges until trial ends!"
        },
        "trial_ending": {
            "subject": "⏰ Your Premium Trial Ends in 2 Days",
            "greeting": "Hi {user_name}!",
            "title": "Trial Ending Soon",
            "message": "Your Premium trial for <strong>{guild_name}</strong> ends in 2 days.",
            "trial_ends": "Trial End Date: {trial_end_date}",
            "continue_message": "Want to continue with Premium? No action needed - your subscription will automatically activate.",
            "cancel_message": "Don't want to continue? Cancel anytime before {trial_end_date}.",
            "cta": "Manage Subscription",
            "footer": "Questions? We're here to help!"
        }
    },
    
    # ========== ARABIC (AR) ==========
    "ar": {
        "subscription_confirmation": {
            "subject": "✅ مرحباً بك في Kingdom-77 البريميوم!",
            "greeting": "مرحباً {user_name}!",
            "title": "مرحباً بك في البريميوم!",
            "message": "شكراً لاشتراكك في Kingdom-77 البريميوم لـ <strong>{guild_name}</strong>.",
            "details": "تفاصيل الاشتراك:",
            "tier": "الباقة",
            "amount": "المبلغ",
            "interval": "الفوترة",
            "next_billing": "تاريخ الفوترة التالية",
            "features_title": "مميزات البريميوم الخاصة بك:",
            "features": [
                "زيادة XP بمقدار 2x لجميع الأعضاء",
                "ألوان مخصصة للرسائل",
                "دعم أولوية",
                "إحصائيات متقدمة",
                "أوامر مخصصة"
            ],
            "cta": "الذهاب إلى لوحة التحكم",
            "footer": "إذا كان لديك أي أسئلة، اتصل بفريق الدعم.",
            "unsubscribe": "إلغاء الاشتراك في الرسائل"
        },
        "subscription_renewal": {
            "subject": "✅ تم تجديد Kingdom-77 البريميوم",
            "greeting": "مرحباً {user_name}!",
            "title": "تم تجديد الاشتراك",
            "message": "تم تجديد اشتراك البريميوم لـ <strong>{guild_name}</strong> بنجاح.",
            "amount_charged": "المبلغ المحصّل: ${amount}",
            "next_billing": "الفوترة التالية: {next_billing_date}",
            "cta": "عرض الاشتراك",
            "footer": "شكراً لدعمك المستمر!"
        },
        "subscription_cancelled": {
            "subject": "❌ تم إلغاء Kingdom-77 البريميوم",
            "greeting": "مرحباً {user_name}!",
            "title": "تم إلغاء الاشتراك",
            "message": "تم إلغاء اشتراك البريميوم لـ <strong>{guild_name}</strong>.",
            "expires_on": "ستظل مميزات البريميوم نشطة حتى: <strong>{expiry_date}</strong>",
            "feedback": "نود سماع سبب الإلغاء. ملاحظاتك تساعدنا على التحسين.",
            "cta": "إعادة تفعيل البريميوم",
            "footer": "نأمل رؤيتك مرة أخرى قريباً!"
        },
        "subscription_expired": {
            "subject": "⏰ انتهت صلاحية Kingdom-77 البريميوم",
            "greeting": "مرحباً {user_name}!",
            "title": "انتهى البريميوم",
            "message": "انتهت صلاحية اشتراك البريميوم لـ <strong>{guild_name}</strong>.",
            "renew_message": "هل تريد الاستمرار في الاستمتاع بمميزات البريميوم؟",
            "cta": "التجديد الآن",
            "footer": "احصل على خصم 10% إذا جددت خلال 7 أيام!"
        },
        "payment_failed": {
            "subject": "⚠️ فشل الدفع - مطلوب إجراء",
            "greeting": "مرحباً {user_name}!",
            "title": "فشل الدفع",
            "message": "لم نتمكن من معالجة دفعتك لاشتراك <strong>{guild_name}</strong> البريميوم.",
            "reason": "السبب: {failure_reason}",
            "action_required": "يرجى تحديث طريقة الدفع لتجنب انقطاع الخدمة.",
            "expiry_warning": "سينتهي اشتراكك في <strong>{expiry_date}</strong> إذا لم يتم استلام الدفع.",
            "cta": "تحديث طريقة الدفع",
            "footer": "تحتاج مساعدة؟ اتصل بفريق الدعم."
        },
        "trial_started": {
            "subject": "🎉 بدأت تجربتك المجانية لمدة 7 أيام!",
            "greeting": "مرحباً {user_name}!",
            "title": "بدأت التجربة!",
            "message": "مرحباً بك في تجربتك المجانية لمدة 7 أيام من Kingdom-77 البريميوم لـ <strong>{guild_name}</strong>!",
            "trial_ends": "تنتهي التجربة: {trial_end_date}",
            "features_title": "استمتع بهذه المميزات البريميوم:",
            "features": [
                "زيادة XP بمقدار 2x",
                "ألوان مخصصة",
                "دعم أولوية",
                "إحصائيات متقدمة",
                "أوامر مخصصة"
            ],
            "auto_renewal": "ستتحول تجربتك تلقائياً إلى اشتراك مدفوع إلا إذا تم إلغاؤها.",
            "cta": "استكشف المميزات",
            "footer": "لا رسوم حتى نهاية التجربة!"
        },
        "trial_ending": {
            "subject": "⏰ تنتهي تجربتك البريميوم خلال يومين",
            "greeting": "مرحباً {user_name}!",
            "title": "التجربة تنتهي قريباً",
            "message": "تنتهي تجربة البريميوم لـ <strong>{guild_name}</strong> خلال يومين.",
            "trial_ends": "تاريخ انتهاء التجربة: {trial_end_date}",
            "continue_message": "تريد الاستمرار مع البريميوم؟ لا حاجة لأي إجراء - سيتم تفعيل اشتراكك تلقائياً.",
            "cancel_message": "لا تريد الاستمرار؟ الغِ في أي وقت قبل {trial_end_date}.",
            "cta": "إدارة الاشتراك",
            "footer": "أسئلة؟ نحن هنا للمساعدة!"
        }
    },
    
    # ========== SPANISH (ES) ==========
    "es": {
        "subscription_confirmation": {
            "subject": "✅ ¡Bienvenido a Kingdom-77 Premium!",
            "greeting": "¡Hola {user_name}!",
            "title": "¡Bienvenido a Premium!",
            "message": "Gracias por suscribirte a Kingdom-77 Premium para <strong>{guild_name}</strong>.",
            "details": "Detalles de la Suscripción:",
            "tier": "Nivel",
            "amount": "Monto",
            "interval": "Facturación",
            "next_billing": "Próxima Fecha de Facturación",
            "features_title": "Tus Funciones Premium:",
            "features": [
                "Impulso de XP 2x para todos los miembros",
                "Colores de embed personalizados",
                "Soporte prioritario",
                "Estadísticas avanzadas",
                "Comandos personalizados"
            ],
            "cta": "Ir al Panel",
            "footer": "Si tienes preguntas, contacta a nuestro equipo de soporte.",
            "unsubscribe": "Cancelar suscripción de correos"
        },
        "subscription_renewal": {
            "subject": "✅ Kingdom-77 Premium Renovado",
            "greeting": "¡Hola {user_name}!",
            "title": "Suscripción Renovada",
            "message": "Tu suscripción Premium para <strong>{guild_name}</strong> se ha renovado exitosamente.",
            "amount_charged": "Monto Cobrado: ${amount}",
            "next_billing": "Próxima Facturación: {next_billing_date}",
            "cta": "Ver Suscripción",
            "footer": "¡Gracias por tu continuo apoyo!"
        },
        "subscription_cancelled": {
            "subject": "❌ Kingdom-77 Premium Cancelado",
            "greeting": "¡Hola {user_name}!",
            "title": "Suscripción Cancelada",
            "message": "Tu suscripción Premium para <strong>{guild_name}</strong> ha sido cancelada.",
            "expires_on": "Tus funciones Premium permanecerán activas hasta: <strong>{expiry_date}</strong>",
            "feedback": "Nos encantaría saber por qué cancelaste. Tu opinión nos ayuda a mejorar.",
            "cta": "Reactivar Premium",
            "footer": "¡Esperamos verte pronto de nuevo!"
        },
        "subscription_expired": {
            "subject": "⏰ Kingdom-77 Premium Expirado",
            "greeting": "¡Hola {user_name}!",
            "title": "Premium Expirado",
            "message": "Tu suscripción Premium para <strong>{guild_name}</strong> ha expirado.",
            "renew_message": "¿Quieres seguir disfrutando de las funciones Premium?",
            "cta": "Renovar Ahora",
            "footer": "¡Obtén 10% de descuento si renuevas dentro de 7 días!"
        },
        "payment_failed": {
            "subject": "⚠️ Pago Fallido - Acción Requerida",
            "greeting": "¡Hola {user_name}!",
            "title": "Pago Fallido",
            "message": "No pudimos procesar tu pago para la suscripción Premium de <strong>{guild_name}</strong>.",
            "reason": "Razón: {failure_reason}",
            "action_required": "Por favor actualiza tu método de pago para evitar la interrupción del servicio.",
            "expiry_warning": "Tu suscripción expirará el <strong>{expiry_date}</strong> si no se recibe el pago.",
            "cta": "Actualizar Método de Pago",
            "footer": "¿Necesitas ayuda? Contacta a nuestro equipo de soporte."
        },
        "trial_started": {
            "subject": "🎉 ¡Tu Prueba Premium de 7 Días Ha Comenzado!",
            "greeting": "¡Hola {user_name}!",
            "title": "¡Prueba Iniciada!",
            "message": "¡Bienvenido a tu prueba gratuita de 7 días de Kingdom-77 Premium para <strong>{guild_name}</strong>!",
            "trial_ends": "La Prueba Termina: {trial_end_date}",
            "features_title": "Disfruta estas funciones Premium:",
            "features": [
                "Impulso de XP 2x",
                "Colores personalizados",
                "Soporte prioritario",
                "Estadísticas avanzadas",
                "Comandos personalizados"
            ],
            "auto_renewal": "Tu prueba se convertirá automáticamente en una suscripción pagada a menos que la canceles.",
            "cta": "Explorar Funciones",
            "footer": "¡Sin cargos hasta que termine la prueba!"
        },
        "trial_ending": {
            "subject": "⏰ Tu Prueba Premium Termina en 2 Días",
            "greeting": "¡Hola {user_name}!",
            "title": "Prueba Terminando Pronto",
            "message": "Tu prueba Premium para <strong>{guild_name}</strong> termina en 2 días.",
            "trial_ends": "Fecha de Fin de Prueba: {trial_end_date}",
            "continue_message": "¿Quieres continuar con Premium? No se necesita acción - tu suscripción se activará automáticamente.",
            "cancel_message": "¿No quieres continuar? Cancela en cualquier momento antes del {trial_end_date}.",
            "cta": "Gestionar Suscripción",
            "footer": "¿Preguntas? ¡Estamos aquí para ayudar!"
        }
    },
    
    # ========== FRENCH (FR) ==========
    "fr": {
        "subscription_confirmation": {
            "subject": "✅ Bienvenue dans Kingdom-77 Premium !",
            "greeting": "Bonjour {user_name} !",
            "title": "Bienvenue dans Premium !",
            "message": "Merci de vous être abonné à Kingdom-77 Premium pour <strong>{guild_name}</strong>.",
            "details": "Détails de l'Abonnement :",
            "tier": "Niveau",
            "amount": "Montant",
            "interval": "Facturation",
            "next_billing": "Prochaine Date de Facturation",
            "features_title": "Vos Fonctionnalités Premium :",
            "features": [
                "Boost XP 2x pour tous les membres",
                "Couleurs d'embed personnalisées",
                "Support prioritaire",
                "Statistiques avancées",
                "Commandes personnalisées"
            ],
            "cta": "Aller au Tableau de Bord",
            "footer": "Si vous avez des questions, contactez notre équipe de support.",
            "unsubscribe": "Se désabonner des emails"
        },
        "subscription_renewal": {
            "subject": "✅ Kingdom-77 Premium Renouvelé",
            "greeting": "Bonjour {user_name} !",
            "title": "Abonnement Renouvelé",
            "message": "Votre abonnement Premium pour <strong>{guild_name}</strong> a été renouvelé avec succès.",
            "amount_charged": "Montant Facturé : ${amount}",
            "next_billing": "Prochaine Facturation : {next_billing_date}",
            "cta": "Voir l'Abonnement",
            "footer": "Merci pour votre soutien continu !"
        },
        "subscription_cancelled": {
            "subject": "❌ Kingdom-77 Premium Annulé",
            "greeting": "Bonjour {user_name} !",
            "title": "Abonnement Annulé",
            "message": "Votre abonnement Premium pour <strong>{guild_name}</strong> a été annulé.",
            "expires_on": "Vos fonctionnalités Premium resteront actives jusqu'au : <strong>{expiry_date}</strong>",
            "feedback": "Nous aimerions savoir pourquoi vous avez annulé. Vos retours nous aident à nous améliorer.",
            "cta": "Réactiver Premium",
            "footer": "Nous espérons vous revoir bientôt !"
        },
        "subscription_expired": {
            "subject": "⏰ Kingdom-77 Premium Expiré",
            "greeting": "Bonjour {user_name} !",
            "title": "Premium Expiré",
            "message": "Votre abonnement Premium pour <strong>{guild_name}</strong> a expiré.",
            "renew_message": "Vous voulez continuer à profiter des fonctionnalités Premium ?",
            "cta": "Renouveler Maintenant",
            "footer": "Obtenez 10% de réduction si vous renouvelez dans les 7 jours !"
        },
        "payment_failed": {
            "subject": "⚠️ Paiement Échoué - Action Requise",
            "greeting": "Bonjour {user_name} !",
            "title": "Paiement Échoué",
            "message": "Nous n'avons pas pu traiter votre paiement pour l'abonnement Premium de <strong>{guild_name}</strong>.",
            "reason": "Raison : {failure_reason}",
            "action_required": "Veuillez mettre à jour votre méthode de paiement pour éviter l'interruption du service.",
            "expiry_warning": "Votre abonnement expirera le <strong>{expiry_date}</strong> si le paiement n'est pas reçu.",
            "cta": "Mettre à Jour le Mode de Paiement",
            "footer": "Besoin d'aide ? Contactez notre équipe de support."
        },
        "trial_started": {
            "subject": "🎉 Votre Essai Premium de 7 Jours a Commencé !",
            "greeting": "Bonjour {user_name} !",
            "title": "Essai Commencé !",
            "message": "Bienvenue dans votre essai gratuit de 7 jours de Kingdom-77 Premium pour <strong>{guild_name}</strong> !",
            "trial_ends": "L'Essai Se Termine : {trial_end_date}",
            "features_title": "Profitez de ces fonctionnalités Premium :",
            "features": [
                "Boost XP 2x",
                "Couleurs personnalisées",
                "Support prioritaire",
                "Statistiques avancées",
                "Commandes personnalisées"
            ],
            "auto_renewal": "Votre essai se convertira automatiquement en abonnement payant sauf annulation.",
            "cta": "Explorer les Fonctionnalités",
            "footer": "Aucun frais jusqu'à la fin de l'essai !"
        },
        "trial_ending": {
            "subject": "⏰ Votre Essai Premium Se Termine dans 2 Jours",
            "greeting": "Bonjour {user_name} !",
            "title": "Essai Se Terminant Bientôt",
            "message": "Votre essai Premium pour <strong>{guild_name}</strong> se termine dans 2 jours.",
            "trial_ends": "Date de Fin d'Essai : {trial_end_date}",
            "continue_message": "Vous voulez continuer avec Premium ? Aucune action nécessaire - votre abonnement s'activera automatiquement.",
            "cancel_message": "Vous ne voulez pas continuer ? Annulez à tout moment avant le {trial_end_date}.",
            "cta": "Gérer l'Abonnement",
            "footer": "Des questions ? Nous sommes là pour vous aider !"
        }
    },
    
    # ========== GERMAN (DE) ==========
    "de": {
        "subscription_confirmation": {
            "subject": "✅ Willkommen bei Kingdom-77 Premium!",
            "greeting": "Hallo {user_name}!",
            "title": "Willkommen bei Premium!",
            "message": "Vielen Dank für dein Abonnement von Kingdom-77 Premium für <strong>{guild_name}</strong>.",
            "details": "Abonnement-Details:",
            "tier": "Stufe",
            "amount": "Betrag",
            "interval": "Abrechnung",
            "next_billing": "Nächstes Abrechnungsdatum",
            "features_title": "Deine Premium-Funktionen:",
            "features": [
                "2x XP-Boost für alle Mitglieder",
                "Benutzerdefinierte Embed-Farben",
                "Prioritäts-Support",
                "Erweiterte Statistiken",
                "Benutzerdefinierte Befehle"
            ],
            "cta": "Zum Dashboard",
            "footer": "Bei Fragen kontaktiere unser Support-Team.",
            "unsubscribe": "Von E-Mails abmelden"
        },
        "subscription_renewal": {
            "subject": "✅ Kingdom-77 Premium Erneuert",
            "greeting": "Hallo {user_name}!",
            "title": "Abonnement Erneuert",
            "message": "Dein Premium-Abonnement für <strong>{guild_name}</strong> wurde erfolgreich erneuert.",
            "amount_charged": "Berechneter Betrag: ${amount}",
            "next_billing": "Nächste Abrechnung: {next_billing_date}",
            "cta": "Abonnement Anzeigen",
            "footer": "Vielen Dank für deine fortgesetzte Unterstützung!"
        },
        "subscription_cancelled": {
            "subject": "❌ Kingdom-77 Premium Gekündigt",
            "greeting": "Hallo {user_name}!",
            "title": "Abonnement Gekündigt",
            "message": "Dein Premium-Abonnement für <strong>{guild_name}</strong> wurde gekündigt.",
            "expires_on": "Deine Premium-Funktionen bleiben aktiv bis: <strong>{expiry_date}</strong>",
            "feedback": "Wir würden gerne wissen, warum du gekündigt hast. Dein Feedback hilft uns zu verbessern.",
            "cta": "Premium Reaktivieren",
            "footer": "Wir hoffen, dich bald wiederzusehen!"
        },
        "subscription_expired": {
            "subject": "⏰ Kingdom-77 Premium Abgelaufen",
            "greeting": "Hallo {user_name}!",
            "title": "Premium Abgelaufen",
            "message": "Dein Premium-Abonnement für <strong>{guild_name}</strong> ist abgelaufen.",
            "renew_message": "Möchtest du weiterhin Premium-Funktionen genießen?",
            "cta": "Jetzt Erneuern",
            "footer": "Erhalte 10% Rabatt, wenn du innerhalb von 7 Tagen erneuerst!"
        },
        "payment_failed": {
            "subject": "⚠️ Zahlung Fehlgeschlagen - Aktion Erforderlich",
            "greeting": "Hallo {user_name}!",
            "title": "Zahlung Fehlgeschlagen",
            "message": "Wir konnten deine Zahlung für das Premium-Abonnement von <strong>{guild_name}</strong> nicht verarbeiten.",
            "reason": "Grund: {failure_reason}",
            "action_required": "Bitte aktualisiere deine Zahlungsmethode, um eine Dienstunterbrechung zu vermeiden.",
            "expiry_warning": "Dein Abonnement läuft am <strong>{expiry_date}</strong> ab, wenn keine Zahlung eingeht.",
            "cta": "Zahlungsmethode Aktualisieren",
            "footer": "Brauchst du Hilfe? Kontaktiere unser Support-Team."
        },
        "trial_started": {
            "subject": "🎉 Deine 7-Tägige Premium-Testversion Hat Begonnen!",
            "greeting": "Hallo {user_name}!",
            "title": "Testversion Gestartet!",
            "message": "Willkommen zu deiner 7-tägigen kostenlosen Testversion von Kingdom-77 Premium für <strong>{guild_name}</strong>!",
            "trial_ends": "Testversion Endet: {trial_end_date}",
            "features_title": "Genieße diese Premium-Funktionen:",
            "features": [
                "2x XP-Boost",
                "Benutzerdefinierte Farben",
                "Prioritäts-Support",
                "Erweiterte Statistiken",
                "Benutzerdefinierte Befehle"
            ],
            "auto_renewal": "Deine Testversion wird automatisch in ein bezahltes Abonnement umgewandelt, sofern nicht gekündigt.",
            "cta": "Funktionen Erkunden",
            "footer": "Keine Gebühren bis zum Ende der Testversion!"
        },
        "trial_ending": {
            "subject": "⏰ Deine Premium-Testversion Endet in 2 Tagen",
            "greeting": "Hallo {user_name}!",
            "title": "Testversion Endet Bald",
            "message": "Deine Premium-Testversion für <strong>{guild_name}</strong> endet in 2 Tagen.",
            "trial_ends": "Enddatum der Testversion: {trial_end_date}",
            "continue_message": "Möchtest du mit Premium fortfahren? Keine Aktion erforderlich - dein Abonnement wird automatisch aktiviert.",
            "cancel_message": "Möchtest du nicht fortfahren? Kündige jederzeit vor dem {trial_end_date}.",
            "cta": "Abonnement Verwalten",
            "footer": "Fragen? Wir sind hier, um zu helfen!"
        }
    }
}


def get_email_template(language: str, template_type: str) -> Dict[str, Any]:
    """
    Get email template for specific language
    
    Args:
        language: Language code (en, ar, es, fr, de)
        template_type: Type of email template
        
    Returns:
        Email template dictionary
    """
    # Default to English if language not supported
    if language not in EMAIL_TEMPLATES:
        language = "en"
    
    # Get template
    templates = EMAIL_TEMPLATES.get(language, EMAIL_TEMPLATES["en"])
    template = templates.get(template_type, {})
    
    return template


def get_supported_languages() -> list:
    """Get list of supported languages"""
    return list(EMAIL_TEMPLATES.keys())
