document.addEventListener('DOMContentLoaded', () => {
    // ビルドタイムスタンプ表示
    fetch('build_timestamp.txt')
        .then(response => response.text())
        .then(timestamp => {
            const utcDate = new Date(timestamp);
            const jstDate = new Date(utcDate.toLocaleString('en-US', { timeZone: 'Asia/Tokyo' }));
            const formattedTime = jstDate.toLocaleString('ja-JP', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                timeZoneName: 'short'
            });
            document.getElementById('build-timestamp-footer').textContent = 'Last build: ' + formattedTime + ' (JST)';
        });
});
