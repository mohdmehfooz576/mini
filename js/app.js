/* =========================================================
   VoteRight - Complete Frontend JavaScript
========================================================= */

const STORAGE = {
    elections: "vr_elections",
    voters: "vr_voters",
    votes: "vr_votes",
    user: "vr_user"
};

/* ================= DEFAULT ELECTIONS ================= */

const DEFAULT_ELECTIONS = [
    {
        id: 1,
        name: "BCA Department Representative",
        description: "Choose your BCA department representative.",
        start: "2026-09-20",
        end: "2026-09-30",
        status: "Active",
        candidates: [
            { id: 101, name: "Aarav Sharma", year: "2nd Year", votes: 0 },
            { id: 102, name: "Priya Verma", year: "2nd Year", votes: 0 },
            { id: 103, name: "Rohan Patel", year: "3rd Year", votes: 0 },
            { id: 104, name: "Sneha Gupta", year: "3rd Year", votes: 0 }
        ]
    },
    {
        id: 2,
        name: "Principal Election",
        description: "Choose the next principal.",
        start: "2026-09-20",
        end: "2026-09-28",
        status: "Active",
        candidates: [
            { id: 201, name: "Dr. Neha Sharma", year: "Candidate", votes: 0 },
            { id: 202, name: "Dr. Rajiv Kumar", year: "Candidate", votes: 0 }
        ]
    },
    {
        id: 3,
        name: "Student Council",
        description: "Elect your student council representative.",
        start: "2026-09-20",
        end: "2026-09-29",
        status: "Active",
        candidates: [
            { id: 301, name: "Riya Kapoor", year: "2nd Year", votes: 0 },
            { id: 302, name: "Aditya Singh", year: "3rd Year", votes: 0 },
            { id: 303, name: "Kavya Jain", year: "2nd Year", votes: 0 }
        ]
    }
];

/* ================= STORAGE ================= */

function getData(key, fallback) {
    const data = localStorage.getItem(key);

    if (!data) {
        return fallback;
    }

    try {
        return JSON.parse(data);
    } catch {
        return fallback;
    }
}

function saveData(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
}

function getElections() {
    return getData(STORAGE.elections, DEFAULT_ELECTIONS);
}

function getVoters() {
    return getData(STORAGE.voters, []);
}

function getVotes() {
    return getData(STORAGE.votes, []);
}

function getCurrentUser() {
    return getData(STORAGE.user, null);
}

/* ================= HELPERS ================= */

function escapeHTML(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function initials(name) {
    return String(name || "User")
        .split(" ")
        .map(x => x[0])
        .slice(0, 2)
        .join("")
        .toUpperCase();
}

function showToast(message) {
    const toast = document.getElementById("toast");

    if (!toast) return;

    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 2500);
}

function pageName() {
    return location.pathname.split("/").pop() || "index.html";
}

function isAdminPage() {
    return location.pathname.includes("/admin/");
}

function requireLogin() {
    const user = getCurrentUser();

    if (!user) {
        location.href = isAdminPage()
            ? "../index.html"
            : "index.html";

        return null;
    }

    return user;
}

function goPage(page) {
    const user = getCurrentUser();

    if (user?.role === "admin" && isAdminPage()) {
        location.href = "../" + page;
    } else {
        location.href = page;
    }
}

/* ================= LOGIN ================= */

let loginMode = "voter";

function setLoginMode(mode) {
    loginMode = mode;

    const hidden = document.getElementById("loginMode");

    if (hidden) {
        hidden.value = mode;
    }

    document.querySelectorAll(".tab").forEach((tab, index) => {
        tab.classList.toggle(
            "active",
            (mode === "voter" && index === 0) ||
            (mode === "admin" && index === 1)
        );
    });
}

function handleLogin(event) {
    event.preventDefault();

    const email = document
        .getElementById("loginEmail")
        .value
        .trim()
        .toLowerCase();

    const password = document
        .getElementById("loginPassword")
        .value;

    const mode =
        document.getElementById("loginMode")?.value ||
        loginMode;

    if (mode === "admin") {

        if (
            email === "admin@voteright.com" &&
            password === "admin123"
        ) {
            const admin = {
                id: "admin",
                name: "Administrator",
                email,
                role: "admin"
            };

            saveData(STORAGE.user, admin);

            location.href = "admin/manage-elections.html";
            return;
        }

        showToast("Invalid admin credentials.");
        return;
    }

    const voters = getVoters();

    const voter = voters.find(
        v =>
            v.email.toLowerCase() === email &&
            v.password === password
    );

    if (!voter) {
        showToast("Invalid voter email or password.");
        return;
    }

    if (voter.status !== "Approved") {
        showToast("Your registration is waiting for admin approval.");
        return;
    }

    const user = {
        ...voter,
        role: "voter"
    };

    saveData(STORAGE.user, user);

    location.href = "dashboard.html";
}

/* ================= REGISTRATION ================= */

function handleRegistration(event) {
    event.preventDefault();

    const name = document.getElementById("regName").value.trim();
    const roll = document.getElementById("regRoll").value.trim();
    const email = document.getElementById("regEmail").value.trim().toLowerCase();
    const mobile = document.getElementById("regMobile").value.trim();
    const department = document.getElementById("regDepartment").value;
    const year = document.getElementById("regYear").value;
    const password = document.getElementById("regPassword").value;
    const confirmPassword =
        document.getElementById("regConfirmPassword").value;

    if (password !== confirmPassword) {
        showToast("Passwords do not match.");
        return;
    }

    const voters = getVoters();

    const exists = voters.some(
        voter =>
            voter.email.toLowerCase() === email ||
            voter.roll.toLowerCase() === roll.toLowerCase()
    );

    if (exists) {
        showToast("Email or roll number already registered.");
        return;
    }

    const voter = {
        id: Date.now(),
        name,
        roll,
        email,
        mobile,
        department,
        year,
        password,
        status: "Pending"
    };

    voters.push(voter);

    saveData(STORAGE.voters, voters);

    showToast("Registration successful. Wait for admin approval.");

    setTimeout(() => {
        location.href = "index.html";
    }, 1500);
}

/* ================= SIDEBAR ================= */

function voterSidebar(active) {
    return `
        <aside class="sidebar">

            <div class="sidebar-brand">
                <div class="logo">✓</div>
                <div>
                    <h2>VoteRight</h2>
                    <span>Voter Panel</span>
                </div>
            </div>

            <div class="nav-title">Menu</div>

            <a class="nav-link ${active === "dashboard" ? "active" : ""}"
               href="dashboard.html">
                Dashboard
            </a>

            <a class="nav-link ${active === "elections" ? "active" : ""}"
               href="elections.html">
                Elections
            </a>

            <a class="nav-link ${active === "votes" ? "active" : ""}"
               href="my-votes.html">
                My Votes
            </a>

            <a class="nav-link ${active === "results" ? "active" : ""}"
               href="results.html">
                Results
            </a>

            <a class="nav-link logout-link"
               href="#" onclick="logout(); return false;">
                Logout
            </a>

        </aside>
    `;
}

function adminSidebar(active) {
    return `
        <aside class="sidebar">

            <div class="sidebar-brand">
                <div class="logo">✓</div>
                <div>
                    <h2>VoteRight</h2>
                    <span>Admin Panel</span>
                </div>
            </div>

            <div class="nav-title">Administration</div>

            <a class="nav-link ${active === "elections" ? "active" : ""}"
               href="manage-elections.html">
                Manage Elections
            </a>

            <a class="nav-link ${active === "voters" ? "active" : ""}"
               href="manage-voters.html">
                Manage Voters
            </a>

            <a class="nav-link ${active === "results" ? "active" : ""}"
               href="#"
               onclick="goPage('results.html'); return false;">
                Results
            </a>

            <a class="nav-link logout-link"
               href="#"
               onclick="logout(); return false;">
                Logout
            </a>

        </aside>
    `;
}

function shell(title, sidebar, content) {
    const user = getCurrentUser();

    return `
        <div class="app-layout">

            ${sidebar}

            <main class="main">

                <header class="topbar">
                    <h2>${escapeHTML(title)}</h2>

                    <div class="user-box">
                        <div class="avatar">
                            ${initials(user?.name)}
                        </div>

                        <div>
                            <strong>${escapeHTML(user?.name || "User")}</strong>
                        </div>
                    </div>
                </header>

                <section class="content">
                    ${content}
                </section>

            </main>

        </div>
    `;
}

function logout() {
    localStorage.removeItem(STORAGE.user);
    location.href = isAdminPage()
        ? "../index.html"
        : "index.html";
}

/* ================= DASHBOARD ================= */

function renderDashboard() {
    const user = requireLogin();

    if (!user) return;

    const app = document.getElementById("app");

    if (user.role === "admin") {
        renderAdminDashboard();
        return;
    }

    const elections = getElections();
    const votes = getVotes();

    const myVotes = votes.filter(
        vote => vote.voterId === user.id
    );

    const active = elections.filter(
        e => e.status === "Active"
    ).length;

    app.innerHTML = shell(
        "Dashboard",
        voterSidebar("dashboard"),
        `
        <div class="stats-grid">

            <div class="stat-card">
                <p>Available Elections</p>
                <h3>${active}</h3>
            </div>

            <div class="stat-card">
                <p>My Votes</p>
                <h3>${myVotes.length}</h3>
            </div>

            <div class="stat-card">
                <p>Total Elections</p>
                <h3>${elections.length}</h3>
            </div>

            <div class="stat-card">
                <p>Account Status</p>
                <h3 style="font-size:20px">Approved</h3>
            </div>

        </div>

        <div class="section-title">
            <h2>Active Elections</h2>
            <a class="btn primary" href="elections.html">
                View All
            </a>
        </div>

        <div class="election-grid">
            ${elections
                .filter(e => e.status === "Active")
                .slice(0, 3)
                .map(electionCard)
                .join("")}
        </div>
        `
    );
}

/* ================= ADMIN DASHBOARD ================= */

function renderAdminDashboard() {
    const voters = getVoters();
    const elections = getElections();
    const votes = getVotes();

    const app = document.getElementById("app");

    app.innerHTML = shell(
        "Admin Dashboard",
        adminSidebar(""),
        `
        <div class="stats-grid">

            <div class="stat-card">
                <p>Total Voters</p>
                <h3>${voters.length}</h3>
            </div>

            <div class="stat-card">
                <p>Total Elections</p>
                <h3>${elections.length}</h3>
            </div>

            <div class="stat-card">
                <p>Total Votes</p>
                <h3>${votes.length}</h3>
            </div>

            <div class="stat-card">
                <p>Active Elections</p>
                <h3>
                    ${elections.filter(e => e.status === "Active").length}
                </h3>
            </div>

        </div>

        <div class="card">
            <h2>Welcome to VoteRight Admin Panel</h2>
            <p style="margin-top:10px;color:#6b7280">
                Manage voters, elections, candidates and results from here.
            </p>

            <div class="actions" style="margin-top:20px">
                <a class="btn primary" href="manage-elections.html">
                    Manage Elections
                </a>

                <a class="btn secondary" href="manage-voters.html">
                    Manage Voters
                </a>
            </div>
        </div>
        `
    );
}

/* ================= ELECTION CARD ================= */

function electionCard(election) {
    const voted = hasVoted(election.id);

    return `
        <div class="election-card">

            <span class="badge ${
                election.status === "Active"
                    ? "active"
                    : "stopped"
            }">
                ${escapeHTML(election.status)}
            </span>

            <h3>${escapeHTML(election.name)}</h3>

            <p>
                ${escapeHTML(election.description)}
            </p>

            <div class="election-meta">
                <strong>Start:</strong> ${election.start}<br>
                <strong>End:</strong> ${election.end}<br>
                <strong>Candidates:</strong> ${election.candidates.length}
            </div>

            ${
                voted
                    ? `<button class="btn secondary full" disabled>
                        Already Voted
                       </button>`
                    : election.status === "Active"
                    ? `<button class="btn primary full"
                        onclick="openVote(${election.id})">
                        Vote Now
                       </button>`
                    : `<button class="btn secondary full" disabled>
                        Election Stopped
                       </button>`
            }

        </div>
    `;
}

/* ================= ELECTIONS ================= */

function renderElections() {
    const user = requireLogin();

    if (!user) return;

    if (user.role === "admin") {
        renderAdminDashboard();
        return;
    }

    const elections = getElections();

    document.getElementById("app").innerHTML = shell(
        "Elections",
        voterSidebar("elections"),
        `
        <div class="section-title">
            <div>
                <h2>Available Elections</h2>
                <p style="color:#6b7280;margin-top:5px">
                    Select an election to cast your vote.
                </p>
            </div>
        </div>

        <div class="election-grid">
            ${
                elections.length
                    ? elections.map(electionCard).join("")
                    : `<div class="empty">No elections available.</div>`
            }
        </div>
        `
    );
}

function openVote(id) {
    location.href = `vote.html?id=${id}`;
}

/* ================= VOTE PAGE ================= */

function renderVotePage() {
    const user = requireLogin();

    if (!user || user.role !== "voter") return;

    const id = Number(
        new URLSearchParams(location.search).get("id")
    );

    const elections = getElections();
    const election = elections.find(e => e.id === id);

    if (!election) {
        document.getElementById("app").innerHTML = shell(
            "Vote",
            voterSidebar("elections"),
            `<div class="empty">Election not found.</div>`
        );
        return;
    }

    if (election.status !== "Active") {
        document.getElementById("app").innerHTML = shell(
            "Vote",
            voterSidebar("elections"),
            `
            <div class="empty">
                <h2>Election Stopped</h2>
                <p style="margin:10px 0 20px">
                    Voting is currently closed for this election.
                </p>

                <a class="btn primary" href="elections.html">
                    Back to Elections
                </a>
            </div>
            `
        );
        return;
    }

    if (hasVoted(election.id)) {
        document.getElementById("app").innerHTML = shell(
            "Vote",
            voterSidebar("elections"),
            `
            <div class="empty">
                <h2>You Already Voted</h2>
                <p style="margin:10px 0 20px">
                    You can cast only one vote in this election.
                </p>

                <a class="btn primary" href="my-votes.html">
                    View My Votes
                </a>
            </div>
            `
        );
        return;
    }

    document.getElementById("app").innerHTML = shell(
        "Cast Your Vote",
        voterSidebar("elections"),
        `
        <div class="card">

            <h2>${escapeHTML(election.name)}</h2>

            <p style="margin:8px 0 25px;color:#6b7280">
                ${escapeHTML(election.description)}
            </p>

            <div class="vote-options">

                ${election.candidates.map(candidate => `
                    <label class="vote-option">

                        <input
                            type="radio"
                            name="candidate"
                            value="${candidate.id}"
                        >

                        <div>
                            <strong>
                                ${escapeHTML(candidate.name)}
                            </strong>

                            <p style="color:#6b7280;margin-top:4px">
                                ${escapeHTML(candidate.year)}
                            </p>
                        </div>

                    </label>
                `).join("")}

            </div>

            <button
                class="btn primary"
                style="margin-top:25px"
                onclick="castVote(${election.id})">
                Submit Vote
            </button>

        </div>
        `
    );
}

function castVote(electionId) {
    const user = getCurrentUser();

    if (!user || user.role !== "voter") {
        location.href = "index.html";
        return;
    }

    const elections = getElections();

    const election = elections.find(
        e => e.id === electionId
    );

    if (!election || election.status !== "Active") {
        showToast("Voting is not available.");
        return;
    }

    if (hasVoted(electionId)) {
        showToast("You have already voted.");
        return;
    }

    const selected = document.querySelector(
        'input[name="candidate"]:checked'
    );

    if (!selected) {
        showToast("Please select a candidate.");
        return;
    }

    const candidateId = Number(selected.value);

    const candidate = election.candidates.find(
        c => c.id === candidateId
    );

    if (!candidate) {
        showToast("Candidate not found.");
        return;
    }

    candidate.votes++;

    saveData(STORAGE.elections, elections);

    const votes = getVotes();

    votes.push({
        id: Date.now(),
        voterId: user.id,
        electionId: election.id,
        electionName: election.name,
        candidateId: candidate.id,
        candidateName: candidate.name,
        date: new Date().toLocaleString()
    });

    saveData(STORAGE.votes, votes);

    showToast("Your vote has been submitted successfully.");

    setTimeout(() => {
        location.href = "my-votes.html";
    }, 1200);
}

/* ================= ONE VOTE CHECK ================= */

function hasVoted(electionId) {
    const user = getCurrentUser();

    if (!user || user.role !== "voter") {
        return false;
    }

    const votes = getVotes();

    return votes.some(
        vote =>
            vote.voterId === user.id &&
            vote.electionId === electionId
    );
}

/* ================= MY VOTES ================= */

function renderMyVotes() {
    const user = requireLogin();

    if (!user || user.role !== "voter") return;

    const votes = getVotes().filter(
        vote => vote.voterId === user.id
    );

    document.getElementById("app").innerHTML = shell(
        "My Votes",
        voterSidebar("votes"),
        `
        ${
            votes.length
                ? `
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr>
                                <th>Election</th>
                                <th>Candidate</th>
                                <th>Date</th>
                            </tr>
                        </thead>

                        <tbody>
                            ${votes.map(vote => `
                                <tr>
                                    <td>${escapeHTML(vote.electionName)}</td>
                                    <td>${escapeHTML(vote.candidateName)}</td>
                                    <td>${escapeHTML(vote.date)}</td>
                                </tr>
                            `).join("")}
                        </tbody>
                    </table>
                </div>
                `
                : `
                <div class="empty">
                    <h2>No Votes Yet</h2>
                    <p style="margin:10px 0 20px">
                        You haven't voted in any election.
                    </p>

                    <a href="elections.html"
                       class="btn primary">
                        View Elections
                    </a>
                </div>
                `
        }
        `
    );
}

/* ================= RESULTS ================= */

function renderResults() {
    const user = requireLogin();

    if (!user) return;

    const elections = getElections();

    document.getElementById("app").innerHTML = shell(
        "Election Results",
        user.role === "admin"
            ? adminSidebar("results")
            : voterSidebar("results"),
        `
        <div class="election-grid">

            ${elections.map(election => {

                const totalVotes =
                    election.candidates.reduce(
                        (sum, c) => sum + c.votes,
                        0
                    );

                return `
                    <div class="card">

                        <span class="badge ${
                            election.status === "Active"
                                ? "active"
                                : "stopped"
                        }">
                            ${election.status}
                        </span>

                        <h2 style="margin:15px 0">
                            ${escapeHTML(election.name)}
                        </h2>

                        ${
                            election.candidates.length
                                ? election.candidates.map(candidate => {

                                    const percentage =
                                        totalVotes === 0
                                            ? 0
                                            : Math.round(
                                                candidate.votes /
                                                totalVotes *
                                                100
                                            );

                                    return `
                                    <div class="result-row">

                                        <div class="result-header">
                                            <strong>
                                                ${escapeHTML(candidate.name)}
                                            </strong>

                                            <span>
                                                ${candidate.votes} votes
                                                (${percentage}%)
                                            </span>
                                        </div>

                                        <div class="progress">
                                            <div
                                                class="progress-bar"
                                                style="width:${percentage}%">
                                            </div>
                                        </div>

                                    </div>
                                    `;

                                }).join("")
                                : `<p>No candidates.</p>`
                        }

                        <strong>
                            Total Votes: ${totalVotes}
                        </strong>

                    </div>
                `;

            }).join("")}

        </div>
        `
    );
}

/* ================= MANAGE VOTERS ================= */

function renderManageVoters() {
    const user = requireLogin();

    if (!user || user.role !== "admin") {
        return;
    }

    const voters = getVoters();

    document.getElementById("app").innerHTML = shell(
        "Manage Voters",
        adminSidebar("voters"),
        `
        <div class="section-title">
            <div>
                <h2>Registered Voters</h2>
                <p style="color:#6b7280;margin-top:5px">
                    Approve or manage voter registrations.
                </p>
            </div>
        </div>

        ${
            voters.length
                ? `
                <div class="table-wrap">
                    <table>

                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Roll No.</th>
                                <th>Email</th>
                                <th>Department</th>
                                <th>Year</th>
                                <th>Status</th>
                                <th>Action</th>
                            </tr>
                        </thead>

                        <tbody>

                            ${voters.map(voter => `
                                <tr>

                                    <td>${escapeHTML(voter.name)}</td>
                                    <td>${escapeHTML(voter.roll)}</td>
                                    <td>${escapeHTML(voter.email)}</td>
                                    <td>${escapeHTML(voter.department)}</td>
                                    <td>${escapeHTML(voter.year)}</td>

                                    <td>
                                        <span class="badge ${
                                            voter.status.toLowerCase()
                                        }">
                                            ${escapeHTML(voter.status)}
                                        </span>
                                    </td>

                                    <td>
                                        <div class="actions">

                                            ${
                                                voter.status === "Pending"
                                                    ? `
                                                    <button
                                                        class="btn success"
                                                        onclick="approveVoter(${voter.id})">
                                                        Approve
                                                    </button>

                                                    <button
                                                        class="btn danger"
                                                        onclick="rejectVoter(${voter.id})">
                                                        Reject
                                                    </button>
                                                    `
                                                    : ""
                                            }

                                            <button
                                                class="btn secondary"
                                                onclick="deleteVoter(${voter.id})">
                                                Delete
                                            </button>

                                        </div>
                                    </td>

                                </tr>
                            `).join("")}

                        </tbody>

                    </table>
                </div>
                `
                : `<div class="empty">No voters registered yet.</div>`
        }
        `
    );
}

function approveVoter(id) {
    const voters = getVoters();

    const voter = voters.find(v => v.id === id);

    if (!voter) return;

    voter.status = "Approved";

    saveData(STORAGE.voters, voters);

    showToast("Voter approved.");

    renderManageVoters();
}

function rejectVoter(id) {
    const voters = getVoters();

    const voter = voters.find(v => v.id === id);

    if (!voter) return;

    voter.status = "Rejected";

    saveData(STORAGE.voters, voters);

    showToast("Voter rejected.");

    renderManageVoters();
}

function deleteVoter(id) {
    if (!confirm("Delete this voter?")) return;

    let voters = getVoters();

    voters = voters.filter(v => v.id !== id);

    saveData(STORAGE.voters, voters);

    showToast("Voter deleted.");

    renderManageVoters();
}

/* ================= MANAGE ELECTIONS ================= */

function renderManageElections() {
    const user = requireLogin();

    if (!user || user.role !== "admin") {
        return;
    }

    const elections = getElections();

    document.getElementById("app").innerHTML = shell(
        "Manage Elections",
        adminSidebar("elections"),
        `
        <div class="section-title">

            <div>
                <h2>Manage Elections</h2>
                <p style="color:#6b7280;margin-top:5px">
                    Create, stop, reopen and manage elections.
                </p>
            </div>

            <button
                class="btn primary"
                onclick="showCreateElectionModal()">
                + Create Election
            </button>

        </div>

        <div class="election-grid">

            ${elections.map(election => `
                <div class="election-card">

                    <span class="badge ${
                        election.status === "Active"
                            ? "active"
                            : "stopped"
                    }">
                        ${election.status}
                    </span>

                    <h3>
                        ${escapeHTML(election.name)}
                    </h3>

                    <p>
                        ${escapeHTML(election.description)}
                    </p>

                    <div class="election-meta">
                        <strong>Start:</strong>
                        ${election.start}<br>

                        <strong>End:</strong>
                        ${election.end}<br>

                        <strong>Candidates:</strong>
                        ${election.candidates.length}
                    </div>

                    <div class="actions">

                        <button
                            class="btn primary"
                            onclick="openCandidates(${election.id})">
                            Candidates
                        </button>

                        <button
                            class="btn secondary"
                            onclick="openResults(${election.id})">
                            Results
                        </button>

                        ${
                            election.status === "Active"
                                ? `
                                <button
                                    class="btn danger"
                                    onclick="stopElection(${election.id})">
                                    Stop Election
                                </button>
                                `
                                : `
                                <button
                                    class="btn success"
                                    onclick="reopenElection(${election.id})">
                                    Reopen
                                </button>
                                `
                        }

                    </div>

                </div>
            `).join("")}

        </div>
        `
    );
}

/* ================= CREATE ELECTION ================= */

function showCreateElectionModal() {
    const modal = document.createElement("div");

    modal.className = "modal";

    modal.innerHTML = `
        <div class="modal-box">

            <div class="modal-header">
                <h2>Create Election</h2>

                <button
                    class="close-btn"
                    onclick="this.closest('.modal').remove()">
                    ×
                </button>
            </div>

            <form id="createElectionForm">

                <label>Election Name</label>
                <input
                    id="newElectionName"
                    placeholder="Enter election name"
                    required
                >

                <label>Description</label>
                <input
                    id="newElectionDescription"
                    placeholder="Enter description"
                    required
                >

                <label>Start Date</label>
                <input
                    type="date"
                    id="newElectionStart"
                    required
                >

                <label>End Date</label>
                <input
                    type="date"
                    id="newElectionEnd"
                    required
                >

                <button
                    type="submit"
                    class="btn primary full">
                    Create Election
                </button>

            </form>

        </div>
    `;

    document.body.appendChild(modal);

    document.getElementById("createElectionForm")
        .addEventListener("submit", createElection);
}

function createElection(event) {
    event.preventDefault();

    const name =
        document.getElementById("newElectionName").value.trim();

    const description =
        document.getElementById("newElectionDescription").value.trim();

    const start =
        document.getElementById("newElectionStart").value;

    const end =
        document.getElementById("newElectionEnd").value;

    if (end < start) {
        showToast("End date cannot be before start date.");
        return;
    }

    const elections = getElections();

    const election = {
        id: Date.now(),
        name,
        description,
        start,
        end,
        status: "Active",
        candidates: []
    };

    elections.push(election);

    saveData(STORAGE.elections, elections);

    document.querySelector(".modal")?.remove();

    showToast("Election created successfully.");

    renderManageElections();

    setTimeout(() => {
        openCandidates(election.id);
    }, 700);
}

/* ================= STOP / REOPEN ================= */

function stopElection(id) {
    if (!confirm(
        "Are you sure you want to stop this election?"
    )) {
        return;
    }

    const elections = getElections();

    const election = elections.find(e => e.id === id);

    if (!election) return;

    election.status = "Stopped";

    saveData(STORAGE.elections, elections);

    showToast("Election stopped successfully.");

    renderManageElections();
}

function reopenElection(id) {
    const elections = getElections();

    const election = elections.find(e => e.id === id);

    if (!election) return;

    election.status = "Active";

    saveData(STORAGE.elections, elections);

    showToast("Election reopened.");

    renderManageElections();
}

/* ================= CANDIDATES ================= */

function openCandidates(id) {
    location.href = `candidates.html?id=${id}`;
}

function openResults(id) {
    location.href = `../results.html?id=${id}`;
}

function renderCandidates() {
    const user = requireLogin();

    if (!user || user.role !== "admin") {
        return;
    }

    const id = Number(
        new URLSearchParams(location.search).get("id")
    );

    const elections = getElections();

    const election = elections.find(
        e => e.id === id
    );

    if (!election) {
        document.getElementById("app").innerHTML = shell(
            "Candidates",
            adminSidebar("elections"),
            `<div class="empty">Election not found.</div>`
        );

        return;
    }

    document.getElementById("app").innerHTML = shell(
        "Candidates",
        adminSidebar("elections"),
        `
        <div class="section-title">

            <div>
                <h2>${escapeHTML(election.name)}</h2>
                <p style="color:#6b7280;margin-top:5px">
                    Manage candidates for this election.
                </p>
            </div>

            <div class="actions">
                <button
                    class="btn secondary"
                    onclick="goPage('manage-elections.html')">
                    Back
                </button>

                <button
                    class="btn primary"
                    onclick="showAddCandidateModal(${election.id})">
                    + Add Candidate
                </button>
            </div>

        </div>

        ${
            election.candidates.length
                ? `
                <div class="candidate-grid">

                    ${election.candidates.map(candidate => `
                        <div class="candidate-card">

                            <div class="candidate-avatar">
                                ${initials(candidate.name)}
                            </div>

                            <h3>
                                ${escapeHTML(candidate.name)}
                            </h3>

                            <p>
                                ${escapeHTML(candidate.year)}
                            </p>

                            <strong>
                                Votes: ${candidate.votes}
                            </strong>

                            <div style="margin-top:15px">

                                ${
                                    candidate.votes > 0
                                        ? `
                                        <button
                                            class="btn secondary"
                                            disabled>
                                            Cannot Delete
                                        </button>
                                        `
                                        : `
                                        <button
                                            class="btn danger"
                                            onclick="deleteCandidate(
                                                ${election.id},
                                                ${candidate.id}
                                            )">
                                            Delete
                                        </button>
                                        `
                                }

                            </div>

                        </div>
                    `).join("")}

                </div>
                `
                : `
                <div class="empty">
                    <h2>No Candidates</h2>
                    <p style="margin-top:10px">
                        Add candidates to start voting.
                    </p>
                </div>
                `
        }
        `
    );
}

function showAddCandidateModal(electionId) {
    const modal = document.createElement("div");

    modal.className = "modal";

    modal.innerHTML = `
        <div class="modal-box">

            <div class="modal-header">

                <h2>Add Candidate</h2>

                <button
                    class="close-btn"
                    onclick="this.closest('.modal').remove()">
                    ×
                </button>

            </div>

            <form id="candidateForm">

                <label>Candidate Name</label>

                <input
                    id="candidateName"
                    placeholder="Enter candidate name"
                    required
                >

                <label>Year / Position</label>

                <input
                    id="candidateYear"
                    placeholder="Example: 2nd Year"
                    required
                >

                <button
                    class="btn primary full"
                    type="submit">
                    Add Candidate
                </button>

            </form>

        </div>
    `;

    document.body.appendChild(modal);

    document.getElementById("candidateForm")
        .addEventListener(
            "submit",
            event => addCandidate(event, electionId)
        );
}

function addCandidate(event, electionId) {
    event.preventDefault();

    const name =
        document.getElementById("candidateName")
            .value.trim();

    const year =
        document.getElementById("candidateYear")
            .value.trim();

    const elections = getElections();

    const election = elections.find(
        e => e.id === electionId
    );

    if (!election) return;

    const duplicate = election.candidates.some(
        c => c.name.toLowerCase() === name.toLowerCase()
    );

    if (duplicate) {
        showToast("Candidate already exists.");
        return;
    }

    election.candidates.push({
        id: Date.now(),
        name,
        year,
        votes: 0
    });

    saveData(STORAGE.elections, elections);

    document.querySelector(".modal")?.remove();

    showToast("Candidate added.");

    renderCandidates();
}

function deleteCandidate(electionId, candidateId) {
    const elections = getElections();

    const election = elections.find(
        e => e.id === electionId
    );

    if (!election) return;

    const candidate = election.candidates.find(
        c => c.id === candidateId
    );

    if (!candidate) return;

    if (candidate.votes > 0) {
        showToast("Candidate with votes cannot be deleted.");
        return;
    }

    if (!confirm(
        `Delete ${candidate.name}?`
    )) {
        return;
    }

    election.candidates =
        election.candidates.filter(
            c => c.id !== candidateId
        );

    saveData(STORAGE.elections, elections);

    showToast("Candidate deleted.");

    renderCandidates();
}

/* ================= INITIALIZATION ================= */

function initializeStorage() {

    if (!localStorage.getItem(STORAGE.elections)) {
        saveData(
            STORAGE.elections,
            DEFAULT_ELECTIONS
        );
    }

    if (!localStorage.getItem(STORAGE.voters)) {
        saveData(STORAGE.voters, []);
    }

    if (!localStorage.getItem(STORAGE.votes)) {
        saveData(STORAGE.votes, []);
    }
}

document.addEventListener("DOMContentLoaded", () => {

    initializeStorage();

    const page = pageName();

    /* LOGIN */

    if (page === "index.html") {

        const user = getCurrentUser();

        if (user) {
            if (user.role === "admin") {
                location.href =
                    "admin/manage-elections.html";
            } else {
                location.href =
                    "dashboard.html";
            }

            return;
        }

        document
            .getElementById("loginForm")
            ?.addEventListener(
                "submit",
                handleLogin
            );

        return;
    }

    /* REGISTER */

    if (page === "register.html") {

        document
            .getElementById("registrationForm")
            ?.addEventListener(
                "submit",
                handleRegistration
            );

        return;
    }

    /* DASHBOARD */

    if (page === "dashboard.html") {
        renderDashboard();
        return;
    }

    /* ELECTIONS */

    if (page === "elections.html") {
        renderElections();
        return;
    }

    /* VOTE */

    if (page === "vote.html") {
        renderVotePage();
        return;
    }

    /* MY VOTES */

    if (page === "my-votes.html") {
        renderMyVotes();
        return;
    }

    /* RESULTS */

    if (page === "results.html") {
        renderResults();
        return;
    }

    /* ADMIN VOTERS */

    if (page === "manage-voters.html") {
        renderManageVoters();
        return;
    }

    /* ADMIN ELECTIONS */

    if (page === "manage-elections.html") {
        renderManageElections();
        return;
    }

    /* ADMIN CANDIDATES */

    if (page === "candidates.html") {
        renderCandidates();
        return;
    }

});