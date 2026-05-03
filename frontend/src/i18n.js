import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
    en: {
        translation: {
            "dashboard": "Institutional Dashboard",
            "ledgers": "Global Ledgers",
            "participants": "Network Participants",
            "audit": "Audit History",
            "verified": "System Verified",
            "issued": "Issued",
            "draft": "Draft",
            "active": "Active",
            "governance": "Network Governance",
            "sblc_lifecycle": "Instrument Lifecycle",
            "trust_verification": "Network Trust Anchor",
            "amendment": "Propose Amendment",
            "create_instrument": "Initialize Instrument",
            "institutional_hierarchy": "Institutional Hierarchy",
            "verify_badge": "Institutional System Verified",
            "explorer": "Network Explorer",
            "sign_out": "Sign Out Session",
            "live": "Live Node",
            "status_distribution": "Status Distribution",
            "total_volume": "Total Liquidity Volume",
            "recent_activity": "Network Activity Stream",
            "onboarding": "Portal Activation",
            "setup_password": "Establish Secure Keys"
        }
    },
    ar: {
        translation: {
            "dashboard": "لوحة القيادة المؤسسية",
            "ledgers": "السجلات العالمية",
            "participants": "المشاركون في الشبكة",
            "audit": "سجل التدقيق",
            "verified": "نظام تم التحقق منه",
            "issued": "صادر",
            "draft": "مسودة",
            "active": "نشط",
            "governance": "حوكمة الشبكة",
            "sblc_lifecycle": "دورة حياة الأداة",
            "trust_verification": "مرساة الثقة في الشبكة",
            "amendment": "اقتراح تعديل",
            "create_instrument": "بدء الأداة",
            "institutional_hierarchy": "التسلسل الهرمي المؤسسي",
            "verify_badge": "نظام مؤسسي تم التحقق منه",
            "explorer": "مستكشف الشبكة",
            "sign_out": "خروج من الجلسة",
            "live": "عقدة نشطة",
            "status_distribution": "توزيع الحالة",
            "total_volume": "إجمالي حجم السيولة",
            "recent_activity": "تدفق نشاط الشبكة",
            "onboarding": "تفعيل البوابة",
            "setup_password": "إنشاء مفاتيح آمنة"
        }
    },
    fr: {
        translation: {
            "dashboard": "Tableau de Bord Institutionnel",
            "ledgers": "Livres de Comptes Globaux",
            "participants": "Participants du Réseau",
            "audit": "Historique d'Audit",
            "verified": "Système Vérifié",
            "issued": "Émis",
            "draft": "Brouillon",
            "active": "Actif"
        }
    },
    de: {
        translation: {
            "dashboard": "Institutionelles Dashboard",
            "ledgers": "Globale Hauptbücher",
            "participants": "Netzwerkteilnehmer",
            "audit": "Prüfprotokoll",
            "verified": "System Verifiziert",
            "issued": "Ausgestellt",
            "active": "Aktiv"
        }
    },
    es: {
        translation: {
            "dashboard": "Panel Institucional",
            "ledgers": "Libros Mayores Globales",
            "participants": "Participantes de la Red",
            "audit": "Historial de Auditoría",
            "verified": "Sistema Verificado",
            "issued": "Emitido",
            "active": "Activo"
        }
    },
    zh: {
        translation: {
            "dashboard": "机构仪表板",
            "ledgers": "全球分类账",
            "participants": "网络参与者",
            "audit": "审计历史",
            "verified": "系统已验证",
            "issued": "已发行",
            "active": "活跃"
        }
    },
    ru: {
        translation: {
            "dashboard": "Институциональная панель",
            "ledgers": "Глобальные реестры",
            "participants": "Участники сети",
            "audit": "История аудита",
            "verified": "Система проверена",
            "issued": "Выпущено",
            "active": "Активно"
        }
    },
    hi: {
        translation: {
            "dashboard": "संस्थागत डैशबोर्ड",
            "ledgers": "वैश्विक बहीखाता",
            "participants": "नेटवर्क प्रतिभागी",
            "audit": "ऑडिट इतिहास",
            "verified": "सिस्टम सत्यापित",
            "issued": "जारी किया गया",
            "active": "सक्रिय"
        }
    }
};

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        fallbackLng: 'en',
        interpolation: {
            escapeValue: false
        },
        detection: {
            order: ['navigator', 'htmlTag', 'path', 'subdomain'],
            caches: ['localStorage', 'cookie']
        }
    });

export default i18n;
