document.addEventListener('DOMContentLoaded', () => {
  console.log('SiteWatcherが起動しました');

  // メッセージを画面に表示
  const messageElement = document.createElement('p');
  messageElement.textContent = 'SiteWatcherが起動しました';
  document.body.appendChild(messageElement);
}); 