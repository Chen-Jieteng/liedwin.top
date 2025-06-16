/**
 * CKEditor图片尺寸修复脚本
 * 这个脚本会在页面加载后直接修改所有CKEditor实例的图片处理行为
 */
(function() {
    // 等待页面完全加载
    window.addEventListener('load', function() {
        console.log('CKEditor图片修复脚本已加载');
        
        // 等待CKEditor实例完全初始化
        setTimeout(fixAllEditors, 1000);
        
        // 每2秒运行一次，确保新添加的图片也会被处理
        setInterval(fixAllEditors, 2000);
    });
    
    // 修复所有编辑器实例中的图片
    function fixAllEditors() {
        // 确保CKEDITOR全局对象已加载
        if (typeof CKEDITOR === 'undefined') {
            console.log('CKEDITOR尚未加载，等待下一次检查');
            return;
        }
        
        console.log('开始检查所有CKEditor实例');
        
        // 遍历所有编辑器实例
        for (var name in CKEDITOR.instances) {
            if (CKEDITOR.instances.hasOwnProperty(name)) {
                var editor = CKEDITOR.instances[name];
                
                try {
                    // 确保编辑器已经完全初始化
                    if (editor && editor.document) {
                        console.log('处理编辑器实例:', name);
                        fixEditorImages(editor);
                        
                        // 监听内容变化
                        if (!editor._imageFixListenerAdded) {
                            editor.on('change', function() {
                                fixEditorImages(this);
                            });
                            
                            // 监听图片添加事件
                            editor.on('contentDom', function() {
                                fixEditorImages(this);
                                
                                // 当编辑区域内容变化时处理图片
                                this.document.on('keyup', function() {
                                    fixEditorImages(editor);
                                });
                                
                                // 当用户粘贴内容时处理图片
                                this.document.on('paste', function() {
                                    setTimeout(function() {
                                        fixEditorImages(editor);
                                    }, 100);
                                });
                            });
                            
                            editor._imageFixListenerAdded = true;
                        }
                    }
                } catch (e) {
                    console.error('处理编辑器实例时出错:', e);
                }
            }
        }
    }
    
    // 修复单个编辑器中的所有图片
    function fixEditorImages(editor) {
        try {
            // 获取编辑器内的document对象
            var doc = editor.document.$;
            if (!doc) return;
            
            // 获取编辑器宽度
            var editorWidth = editor.container.$.clientWidth;
            console.log('编辑器宽度:', editorWidth);
            
            // 查找所有图片元素
            var images = doc.querySelectorAll('img');
            console.log('找到', images.length, '张图片');
            
            // 处理每个图片
            for (var i = 0; i < images.length; i++) {
                var img = images[i];
                
                // 设置为自适应宽度，不超过编辑器宽度
                img.style.maxWidth = '98%';
                img.style.width = 'auto';
                img.style.height = 'auto';
                img.style.display = 'block';
                img.style.margin = '10px auto';
                
                // 移除可能干扰的属性
                img.removeAttribute('width');
                img.removeAttribute('height');
                
                // 处理CKEditor widget
                var parent = img.parentNode;
                if (parent && parent.classList && parent.classList.contains('cke_widget_element')) {
                    parent.style.maxWidth = '98%';
                    parent.style.width = 'auto';
                    parent.removeAttribute('width');
                    parent.removeAttribute('height');
                }
            }
            
            // 直接向editor的iframe head中注入CSS
            injectCssToEditor(editor);
            
        } catch (e) {
            console.error('修复图片时出错:', e);
        }
    }
    
    // 向编辑器的iframe中注入CSS
    function injectCssToEditor(editor) {
        try {
            var iframeDocument = editor.document.$;
            
            // 检查是否已经注入过CSS
            if (iframeDocument._cssInjected) return;
            
            // 创建style元素
            var style = iframeDocument.createElement('style');
            style.type = 'text/css';
            style.innerHTML = `
                img {
                    max-width: 98% !important; 
                    width: auto !important;
                    height: auto !important;
                    display: block !important;
                    margin: 10px auto !important;
                }
                
                .cke_widget_element,
                .cke_widget_wrapper,
                [data-widget="image"] {
                    max-width: 98% !important;
                    width: auto !important;
                }
            `;
            
            // 添加到iframe的head中
            iframeDocument.head.appendChild(style);
            iframeDocument._cssInjected = true;
            
            console.log('成功向编辑器注入CSS');
        } catch (e) {
            console.error('注入CSS时出错:', e);
        }
    }
    
    // 安全的向CKEditor添加图片规则，不直接覆盖任何现有插件
    function setupImageDialogHook() {
        // 确保CKEDITOR已加载
        if (typeof CKEDITOR === 'undefined') return;
        
        try {
            // 监听对话框打开事件
            CKEDITOR.on('dialogDefinition', function(ev) {
                // 确认这是图片对话框
                if (ev.data.name == 'image' || ev.data.name == 'image2') {
                    var dialogDefinition = ev.data.definition;
                    
                    // 修改信息标签页
                    var infoTab = dialogDefinition.getContents('info');
                    if (infoTab) {
                        // 获取宽度字段
                        var widthField = infoTab.get('width');
                        if (widthField) {
                            // 保留原始验证函数
                            var originalValidate = widthField.validate;
                            
                            // 设置新的验证函数，在原始验证后执行我们的逻辑
                            widthField.validate = function() {
                                var result = originalValidate ? originalValidate.apply(this, arguments) : true;
                                return result;
                            };
                            
                            // 清除默认值
                            widthField.default = '';
                        }
                        
                        // 获取高度字段
                        var heightField = infoTab.get('height');
                        if (heightField) {
                            // 清除默认值，让其保持为auto
                            heightField.default = '';
                        }
                    }
                    
                    console.log('成功修改图片对话框默认行为');
                }
            });
        } catch (e) {
            console.error('设置图片对话框钩子时出错:', e);
        }
    }
    
    // 设置对话框钩子
    setTimeout(setupImageDialogHook, 500);
})(); 