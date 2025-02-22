document.addEventListener('DOMContentLoaded', () => {
    // ビルドタイムスタンプ表示
    fetch('build_timestamp.txt')
        .then(response => response.text())
        .then(timestamp => {
            document.getElementById('build-timestamp-footer').textContent = 'Last build: ' + timestamp;
        });
});
