import { escapeHtml, formatDate } from '/static/js/utils.js';

export function initUserPosts({ userId, limit, hasMore, urls }) {
  let currentOffset = limit;

  const postsContainer = document.getElementById('postsContainer');
  const loadMoreBtn = document.getElementById('loadMoreBtn');

  function url(template, value) {
    return template.replace(/__\w+__/, value);
  }

  function createPostHTML(post) {
    return `
      <article class="content-section py-3 px-4 mb-4">
        <div class="d-flex align-items-start gap-4">
          <img class="rounded-circle article-img flex-shrink-0"
               src="${post.author.image_path}"
               alt="${escapeHtml(post.author.username)}'s profile picture"
               width="64" height="64" loading="lazy">
          <div class="flex-grow-1">
            <div class="article-metadata mb-2">
              <a class="me-2" href="${url(urls.userPosts, post.author.id)}">
                ${escapeHtml(post.author.username)}
              </a>
              <small class="text-body-secondary">
                ${formatDate(post.date_posted)}
              </small>
            </div>
            <h2>
              <a class="article-title" href="${url(urls.postPage, post.id)}">
                ${escapeHtml(post.title)}
              </a>
            </h2>
            <p class="article-content">${escapeHtml(post.content)}</p>
          </div>
        </div>
      </article>
    `;
  }

  async function loadMorePosts() {
    loadMoreBtn.disabled = true;
    loadMoreBtn.textContent = 'Loading...';

    try {
      const response = await fetch(`/api/users/${userId}/posts?skip=${currentOffset}&limit=${limit}`);
      const data = await response.json();

      for (const post of data.posts) {
        postsContainer.insertAdjacentHTML('beforeend', createPostHTML(post));
      }

      currentOffset += data.posts.length;

      if (!data.has_more) {
        loadMoreBtn.classList.add('d-none');
      } else {
        loadMoreBtn.disabled = false;
        loadMoreBtn.textContent = 'Load More Posts';
      }
    } catch {
      loadMoreBtn.textContent = 'Error - Click to Retry';
      loadMoreBtn.disabled = false;
    }
  }

  if (loadMoreBtn) {
    loadMoreBtn.addEventListener('click', loadMorePosts);
  }
}