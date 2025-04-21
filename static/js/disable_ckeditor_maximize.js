/**
 * 禁用CKEditor最大化按钮
 * 这个脚本通过多种方式确保CKEditor中的最大化按钮被移除
 */

(function() {
    // 在页面加载完成后执行
    document.addEventListener('DOMContentLoaded', function() {
        // 通过CSS隐藏最大化按钮
        var style = document.createElement('style');
        style.textContent = `
            /* 隐藏CKEditor最大化按钮 */
            .cke_button__maximize,
            .cke_button_icon.cke_button__maximize_icon,
            a[title*="maximize"], 
            a[title*="Maximize"],
            .cke_button[title*="Maximize"],
            .cke_toolbar a[title*="maximize"],
            .cke_toolgroup a[data-cke-tooltip-text*="maximize"],
            .cke_button[aria-label*="Maximize"] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                width: 0 !important;
                height: 0 !important;
                position: absolute !important;
                pointer-events: none !important;
            }
        `;
        document.head.appendChild(style);
        
        // 定期检查并移除最大化按钮
        function removeMaximizeButtons() {
            var selectors = [
                '.cke_button__maximize',
                '.cke_button_icon.cke_button__maximize_icon',
                'a[title*="maximize"]',
                'a[title*="Maximize"]',
                '.cke_button[title*="Maximize"]',
                '.cke_toolbar a[title*="maximize"]',
                '.cke_toolgroup a[data-cke-tooltip-text*="maximize"]',
                '.cke_button[aria-label*="Maximize"]'
            ];
            
            // 合并所有选择器
            var combinedSelector = selectors.join(',');
            
            // 使用原生JavaScript移除按钮
            document.querySelectorAll(combinedSelector).forEach(function(element) {
                if (element && element.parentNode) {
                    element.parentNode.removeChild(element);
                    console.log('找到并移除了CKEditor最大化按钮');
                }
            });
            
            // 如果页面上有jQuery，也用jQuery尝试移除
            if (window.jQuery) {
                jQuery(combinedSelector).remove();
            }
        }
        
        // 立即执行一次
        removeMaximizeButtons();
        
        // 延迟执行，确保能捕获动态加载的编辑器
        setTimeout(removeMaximizeButtons, 500);
        setTimeout(removeMaximizeButtons, 1000);
        setTimeout(removeMaximizeButtons, 2000);
        
        // 如果存在CKEditor全局对象，监听编辑器实例创建事件
        if (window.CKEDITOR) {
            CKEDITOR.on('instanceReady', function(event) {
                var editor = event.editor;
                
                // 尝试禁用最大化命令
                if (editor.commands && editor.commands.maximize) {
                    editor.commands.maximize.disable();
                }
                
                // 移除工具栏中的最大化按钮
                setTimeout(function() {
                    removeMaximizeButtons();
                }, 100);
            });
        }
        
        // 监听DOM变化，以便处理动态加载的编辑器
        if (window.MutationObserver) {
            var observer = new MutationObserver(function(mutations) {
                removeMaximizeButtons();
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: false,
                characterData: false
            });
        }
    });
})(); 