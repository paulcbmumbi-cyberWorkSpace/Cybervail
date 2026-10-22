const menuToggle = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#primary-navigation');
const filterButtons = document.querySelectorAll('[data-alert-filter]');
const alertCards = document.querySelectorAll('[data-alert-category]');
const filterCount = document.querySelector('.filter-count');
const feedStatus = document.querySelector('#feed-status');
const feedChecked = document.querySelector('#feed-checked');
const feedMatchCount = document.querySelector('#feed-match-count');
const feedScannedCount = document.querySelector('#feed-scanned-count');
const feedMessage = document.querySelector('#feed-message');
const phishingResults = document.querySelector('#phishing-results');
const feedRefresh = document.querySelector('#feed-refresh');

if (menuToggle && navigation) {
    const setMenuOpen = (isOpen) => {
        menuToggle.classList.toggle('is-open', isOpen);
        navigation.classList.toggle('is-open', isOpen);
        menuToggle.setAttribute('aria-expanded', String(isOpen));
        menuToggle.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
        document.body.classList.toggle('menu-open', isOpen);
    };

    menuToggle.addEventListener('click', () => {
        setMenuOpen(menuToggle.getAttribute('aria-expanded') !== 'true');
    });

    navigation.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', () => setMenuOpen(false));
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
            setMenuOpen(false);
            menuToggle.focus();
        }
    });

    window.matchMedia('(min-width: 901px)').addEventListener('change', (event) => {
        if (event.matches) {
            setMenuOpen(false);
        }
    });
}

const updateVisibleAlerts = (category) => {
    let visibleCount = 0;

    alertCards.forEach((card) => {
        const isVisible = category === 'all' || card.dataset.alertCategory === category;
        card.hidden = !isVisible;
        visibleCount += Number(isVisible);
    });

    if (filterCount) {
        filterCount.textContent = `${visibleCount} ${visibleCount === 1 ? 'example' : 'examples'}`;
    }
};

filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
        const category = button.dataset.alertFilter;
        filterButtons.forEach((filterButton) => {
            const isActive = filterButton === button;
            filterButton.classList.toggle('is-active', isActive);
            filterButton.setAttribute('aria-pressed', String(isActive));
        });
        updateVisibleAlerts(category);
    });
});

updateVisibleAlerts('all');

const formatFeedTime = (timestamp) => {
    const date = new Date(timestamp);
    if (Number.isNaN(date.getTime())) {
        return 'Unavailable';
    }
    return new Intl.DateTimeFormat(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
    }).format(date);
};

const renderPhishingEntries = (entries) => {
    phishingResults.replaceChildren();

    if (!entries.length) {
        return;
    }

    const list = document.createElement('ul');
    list.className = 'feed-list';

    entries.forEach((entry) => {
        const item = document.createElement('li');
        item.className = 'feed-entry';

        const domain = document.createElement('code');
        domain.textContent = entry.domain;

        const indicator = document.createElement('span');
        indicator.className = 'feed-indicator';
        indicator.textContent = entry.indicator;

        const safetyNote = document.createElement('span');
        safetyNote.className = 'feed-entry-note';
        safetyNote.textContent = 'Not a verified attribution';

        item.append(domain, indicator, safetyNote);
        list.append(item);
    });

    phishingResults.append(list);
};

const loadPhishingFeed = async () => {
    if (!feedStatus) {
        return;
    }

    feedRefresh.disabled = true;
    feedRefresh.textContent = 'Checking…';
    feedStatus.dataset.status = 'loading';
    feedStatus.textContent = 'Checking public feed…';
    feedMessage.textContent = 'Loading Zambia-indicator entries from the public feed.';
    feedMessage.hidden = false;

    try {
        const response = await fetch('/api/zambia-phishing/', {
            headers: { Accept: 'application/json' },
            cache: 'no-store',
        });
        if (!response.ok) {
            throw new Error(`Feed request failed (${response.status}).`);
        }

        const data = await response.json();
        feedStatus.dataset.status = data.status;
        feedStatus.textContent = data.status === 'live'
            ? 'Feed available'
            : data.status === 'stale'
                ? 'Showing last successful snapshot'
                : 'Feed unavailable';
        feedChecked.textContent = formatFeedTime(data.checked_at);
        feedChecked.dateTime = data.checked_at;
        feedMatchCount.textContent = String(data.match_count);
        feedScannedCount.textContent = new Intl.NumberFormat().format(data.feed_entries_scanned);
        renderPhishingEntries(data.entries);

        if (data.status === 'unavailable' || data.status === 'stale') {
            feedMessage.textContent = data.error;
            feedMessage.hidden = false;
        } else if (data.match_count === 0) {
            feedMessage.textContent = 'No entries with the configured Zambia indicators were found in this feed snapshot.';
            feedMessage.hidden = false;
        } else {
            feedMessage.textContent = `Showing ${data.entries.length} of ${data.match_count} matching domains.`;
            feedMessage.hidden = false;
        }
    } catch (error) {
        feedStatus.dataset.status = 'unavailable';
        feedStatus.textContent = 'Feed unavailable';
        feedMessage.textContent = 'Could not load the phishing feed. Please try again later.';
        feedMessage.hidden = false;
        phishingResults.replaceChildren();
        console.error('Could not load the Zambia phishing feed:', error);
    } finally {
        feedRefresh.disabled = false;
        feedRefresh.textContent = 'Check feed';
    }
};

if (feedRefresh && feedStatus) {
    feedRefresh.addEventListener('click', loadPhishingFeed);
    loadPhishingFeed();
    window.setInterval(loadPhishingFeed, 15 * 60 * 1000);
}
