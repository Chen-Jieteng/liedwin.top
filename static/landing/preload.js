// 预加载关键资源和移动端优化
(function() {
    // 检测移动设备
    const isMobile = window.innerWidth <= 768;
    
    // 预加载关键 CSS
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'style';
    link.href = document.querySelector('link[rel="stylesheet"]').href;
    document.head.appendChild(link);
    
    // 移动端优化：延迟加载非关键图片
    if (isMobile) {
        // 添加 loading 提示
        const loadingDiv = document.createElement('div');
        loadingDiv.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
                        background: white; z-index: 9999; display: flex; 
                        align-items: center; justify-content: center; font-family: Arial;">
                <div style="text-align: center;">
                    <div style="width: 40px; height: 40px; border: 4px solid #f3f3f3; 
                                border-top: 4px solid #3498db; border-radius: 50%; 
                                animation: spin 1s linear infinite; margin: 0 auto 20px;"></div>
                    <div style="color: #666;">正在加载芥尘智慧助手...</div>
                </div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        document.body.appendChild(loadingDiv);
        
        // 3秒后移除加载提示
        setTimeout(() => {
            if (loadingDiv.parentNode) {
                loadingDiv.parentNode.removeChild(loadingDiv);
            }
        }, 3000);
    }
    
    // 连接检测
    if ('connection' in navigator) {
        const connection = navigator.connection;
        if (connection.effectiveType === '2g' || connection.effectiveType === 'slow-2g') {
            console.log('检测到慢速网络，启用优化模式');
            // 可以在这里添加更多的优化策略
        }
    }
})(); 