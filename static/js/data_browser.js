document.addEventListener('DOMContentLoaded', function () {
  const links = document.querySelectorAll('.data-file-link');
  const previewArea = document.getElementById('preview-area');
  const previewTitle = document.getElementById('preview-title');
  const downloadLink = document.getElementById('download-link');

  function setLoading() {
    previewArea.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
  }

  async function loadPreview(filename) {
    setLoading();
    previewTitle.textContent = filename;
    downloadLink.style.display = 'none';
    try {
      const url = new URL(window.location.origin + '/data_browser/preview');
      url.searchParams.set('name', filename);
      const resp = await fetch(url);
      if (!resp.ok) {
        const text = await resp.text();
        previewArea.innerHTML = '<div class="alert alert-danger">Error loading file: ' + resp.status + ' ' + text + '</div>';
        return;
      }
      const html = await resp.text();
      previewArea.innerHTML = html;
      // show download link
      downloadLink.href = '/data_browser/download/' + encodeURIComponent(filename);
      downloadLink.style.display = 'inline-block';
    } catch (err) {
      previewArea.innerHTML = '<div class="alert alert-danger">Error: ' + err.message + '</div>';
    }
  }

  links.forEach(function (a) {
    a.addEventListener('click', function (ev) {
      ev.preventDefault();
      const fname = this.dataset.fname;
      if (!fname) return;
      // mark active
      links.forEach(l=> l.classList.remove('active'));
      this.classList.add('active');
      loadPreview(fname);
    });
  });

  // auto-select first file if present
  if (links.length > 0) {
    const first = links[0];
    first.classList.add('active');
    loadPreview(first.dataset.fname);
  }
});