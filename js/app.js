/* =========================================================
   VoteRight - Common Application JavaScript
   Backend Connected Version
========================================================= */


/* =========================================================
   BACKEND URL
========================================================= */

const API_BASE_URL = "";


/* =========================================================
   LOCAL STORAGE KEYS
========================================================= */

const TOKEN_KEY = "vr_token";
const USER_KEY = "vr_user";


/* =========================================================
   AUTH HELPERS
========================================================= */

function getToken() {

    return localStorage.getItem(
        TOKEN_KEY
    );

}


function getCurrentUser() {

    const user =
        localStorage.getItem(
            USER_KEY
        );

    if (!user) {

        return null;

    }

    try {

        return JSON.parse(
            user
        );

    } catch (error) {

        console.error(
            "User data error:",
            error
        );

        return null;

    }

}


function isLoggedIn() {

    return !!getToken();

}


function isAdmin() {

    const user =
        getCurrentUser();

    return (
        user &&
        user.role === "admin"
    );

}


function isVoter() {

    const user =
        getCurrentUser();

    return (
        user &&
        user.role === "voter"
    );

}


/* =========================================================
   AUTH HEADERS
========================================================= */

function authHeaders() {

    const token =
        getToken();


    return {

        "Content-Type":
            "application/json",

        "Authorization":
            "Bearer " + token

    };

}


/* =========================================================
   LOGOUT
========================================================= */

function logout() {

    localStorage.removeItem(
        TOKEN_KEY
    );

    localStorage.removeItem(
        USER_KEY
    );

    window.location.href =
        getRootPath() + "index.html";

}


/* =========================================================
   ROOT PATH
========================================================= */

function getRootPath() {

    const path =
        window.location.pathname;


    if (
        path.includes(
            "/admin/"
        )
    ) {

        return "../";

    }


    return "";

}


/* =========================================================
   PAGE NAVIGATION
========================================================= */

function goPage(
    page
) {

    const root =
        getRootPath();


    window.location.href =
        root + page;

}


/* =========================================================
   ADMIN PAGE CHECK
========================================================= */

function isAdminPage() {

    return window.location.pathname
        .includes(
            "/admin/"
        );

}


/* =========================================================
   AUTHENTICATION GUARD
========================================================= */

function requireLogin() {

    if (
        !getToken() ||
        !getCurrentUser()
    ) {

        window.location.href =
            getRootPath() +
            "index.html";

        return false;

    }

    return true;

}


/* =========================================================
   ADMIN GUARD
========================================================= */

function requireAdmin() {

    if (
        !requireLogin()
    ) {

        return false;

    }


    if (
        !isAdmin()
    ) {

        window.location.href =
            getRootPath() +
            "dashboard.html";

        return false;

    }


    return true;

}


/* =========================================================
   VOTER GUARD
========================================================= */

function requireVoter() {

    if (
        !requireLogin()
    ) {

        return false;

    }


    if (
        !isVoter()
    ) {

        window.location.href =
            getRootPath() +
            "index.html";

        return false;

    }


    return true;

}


/* =========================================================
   API REQUEST HELPER
========================================================= */

async function apiRequest(
    endpoint,
    options = {}
) {

    const requestOptions = {

        ...options,

        headers: {

            ...(options.headers || {}),

            "Authorization":
                "Bearer " + getToken()

        }

    };


    /*
     * Automatically add JSON header
     * when body is JSON.
     */

    if (
        options.body &&
        typeof options.body === "string"
    ) {

        requestOptions.headers[
            "Content-Type"
        ] =
            "application/json";

    }


    const response =
        await fetch(
            API_BASE_URL +
            endpoint,
            requestOptions
        );


    let data = null;


    try {

        data =
            await response.json();

    } catch (error) {

        data = {};

    }


    /*
     * Token expired / invalid
     */

    if (
        response.status === 401
    ) {

        localStorage.removeItem(
            TOKEN_KEY
        );

        localStorage.removeItem(
            USER_KEY
        );


        window.location.href =
            getRootPath() +
            "index.html";


        throw new Error(
            "Your session has expired. Please login again."
        );

    }


    if (
        !response.ok
    ) {

        throw new Error(
            data.message ||
            "Something went wrong."
        );

    }


    return data;

}


/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHTML(
    value
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        value ?? "";


    return div.innerHTML;

}


/* =========================================================
   FORMAT DATE
========================================================= */

function formatDate(
    dateValue
) {

    if (!dateValue) {

        return "-";

    }


    const date =
        new Date(
            dateValue
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {

        return String(
            dateValue
        );

    }


    return date.toLocaleString(
        "en-IN",
        {
            dateStyle: "medium",
            timeStyle: "short"
        }
    );

}


/* =========================================================
   TOAST MESSAGE
========================================================= */

function showToast(
    message,
    type = "success"
) {

    let toast =
        document.getElementById(
            "vrToast"
        );


    if (!toast) {

        toast =
            document.createElement(
                "div"
            );

        toast.id =
            "vrToast";


        toast.style.position =
            "fixed";

        toast.style.right =
            "20px";

        toast.style.bottom =
            "20px";

        toast.style.padding =
            "14px 20px";

        toast.style.borderRadius =
            "10px";

        toast.style.color =
            "#ffffff";

        toast.style.zIndex =
            "9999";

        toast.style.fontSize =
            "14px";

        toast.style.boxShadow =
            "0 5px 20px rgba(0,0,0,0.15)";


        document.body.appendChild(
            toast
        );

    }


    toast.textContent =
        message;


    if (
        type === "error"
    ) {

        toast.style.background =
            "#dc3545";

    } else if (
        type === "warning"
    ) {

        toast.style.background =
            "#ffc107";

        toast.style.color =
            "#000000";

    } else {

        toast.style.background =
            "#198754";

    }


    toast.style.display =
        "block";


    clearTimeout(
        toast._timeout
    );


    toast._timeout =
        setTimeout(
            function() {

                toast.style.display =
                    "none";

            },
            3000
        );

}


/* =========================================================
   CONFIRM ACTION
========================================================= */

function confirmAction(
    message
) {

    return window.confirm(
        message
    );

}


/* =========================================================
   URL QUERY PARAMETER
========================================================= */

function getQueryParam(
    name
) {

    const params =
        new URLSearchParams(
            window.location.search
        );


    return params.get(
        name
    );

}


/* =========================================================
   PAGE REDIRECT AFTER LOGIN
========================================================= */

function redirectAfterLogin(
    user
) {

    if (!user) {

        return;

    }


    if (
        user.role === "admin"
    ) {

        window.location.href =
            "admin/manage-elections.html";

        return;

    }


    window.location.href =
        "dashboard.html";

}


/* =========================================================
   CURRENT USER DISPLAY
========================================================= */

function displayCurrentUser() {

    const user =
        getCurrentUser();


    if (!user) {

        return;

    }


    const nameElements =
        document.querySelectorAll(
            "[data-user-name]"
        );


    nameElements.forEach(
        function(element) {

            element.textContent =
                user.name || "User";

        }
    );


    const emailElements =
        document.querySelectorAll(
            "[data-user-email]"
        );


    emailElements.forEach(
        function(element) {

            element.textContent =
                user.email || "";

        }
    );

}


/* =========================================================
   AUTO DISPLAY USER
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function() {

        displayCurrentUser();

    }
);