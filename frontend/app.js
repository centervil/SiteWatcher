document.addEventListener('DOMContentLoaded', () => {
  console.log('SiteWatcherが起動しました');

  // メッセージを画面に表示
  const messageElement = document.createElement('p');
  messageElement.textContent = 'SiteWatcherが起動しました';
  document.body.appendChild(messageElement);

  // ビルド日時を表示
  fetch('build_timestamp.txt')
    .then(response => response.text())
    .then(timestamp => {
      document.getElementById('build-timestamp').textContent = timestamp.trim();
    })
    .catch(error => {
      console.error('Error fetching build timestamp:', error);
      document.getElementById('build-timestamp').textContent = 'ビルド日時取得エラー';
    });

  // 現在時刻を表示
  const currentTimeElement = document.getElementById('current-time');
  if (currentTimeElement) {
    currentTimeElement.textContent = new Date().toLocaleString();
  }
});
