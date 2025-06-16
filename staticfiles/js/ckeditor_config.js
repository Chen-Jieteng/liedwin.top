// 获取CSRF令牌
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// 定义CKEditor特定配置
CKEDITOR.editorConfig = function(config) {
    // 配置上传URL
    config.filebrowserUploadUrl = '/ckeditor/upload/';
    config.filebrowserBrowseUrl = '/ckeditor/browse/';
    
    // 粘贴上传相关设置
    config.uploadUrl = '/ckeditor/upload/';
    config.imageUploadUrl = '/ckeditor/upload/';
    config.pasteUploadFileApi = '/ckeditor/upload/';
    
    // 允许所有内容
    config.allowedContent = true;
    config.removeFormatAttributes = '';
    
    // 图片预览文本
    config.image_previewText = ' ';
    
    // 图片相关配置
    config.image2_alignClasses = ['image-left', 'image-center', 'image-right'];
    config.image2_disableResizer = false;
    config.image2_prefillDimensions = false; // 不自动填写宽高属性
    config.image_prefillDimensions = false;  // 不自动填写宽高属性
    
    // 添加格式化选项，支持标题
    config.format_tags = 'p;h1;h2;h3;h4;h5;h6;pre';
    
    // 添加CSRF令牌到上传请求
    config.extraPlugins = 'uploadimage,clipboard,dialogadvtab,image2';
    
    // 禁用最大化插件，确保从三个位置移除该功能
    config.removePlugins = 'maximize';
    config.plugins = config.plugins.replace(/maximize,?/, '');
    
    // 自定义工具栏
    config.toolbar = [
        { name: 'document', items: ['Source'] },
        { name: 'clipboard', items: ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord', '-', 'Undo', 'Redo'] },
        { name: 'editing', items: ['Find', 'Replace', '-', 'SelectAll'] },
        { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript', '-', 'RemoveFormat'] },
        '/',
        { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
        { name: 'links', items: ['Link', 'Unlink', 'Anchor'] },
        { name: 'insert', items: ['Image', 'Table', 'HorizontalRule', 'SpecialChar'] },
        '/',
        { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
        { name: 'colors', items: ['TextColor', 'BGColor'] },
        { name: 'tools', items: ['ShowBlocks'] }
    ];
    
    // 设置编辑器宽度与其他表单元素保持一致
    config.width = '100%';
    config.height = '400px';
    
    // 图片上传前添加CSRF令牌
    config.on = {
        instanceReady: function(evt) {
            const editor = evt.editor;
            
            // 禁用最大化按钮 - 直接从DOM中移除按钮
            try {
                // 获取编辑器UI中的最大化按钮并移除
                const maximizeBtn = editor.container.findOne('.cke_button__maximize');
                if (maximizeBtn) {
                    maximizeBtn.remove();
                }
                
                // 如果按钮在父元素中，移除整个父元素
                const maximizeBtnParent = editor.container.findOne('.cke_button__maximize_icon')?.getParent();
                if (maximizeBtnParent) {
                    maximizeBtnParent.remove();
                }
                
                console.log('Maximize button successfully removed from CKEditor');
            } catch (e) {
                console.error('Failed to remove maximize button:', e);
            }
            
            // 为所有AJAX请求添加CSRF令牌
            editor.on('fileUploadRequest', function(evt) {
                const xhr = evt.data.fileLoader.xhr;
                const csrftoken = getCookie('csrftoken');
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            });
            
            // 调整编辑器容器样式
            var editorElement = editor.element.getParent();
            if (editorElement) {
                editorElement.setStyle('width', '100%');
            }
            
            // 直接向编辑器的iframe内注入CSS样式
            try {
                // 获取编辑器的document对象
                var editorDocument = editor.document.$;
                
                // 创建一个新的style元素
                var styleElement = editorDocument.createElement('style');
                styleElement.type = 'text/css';
                
                // 定义强制应用于所有图片的CSS
                var cssRules = `
                    img, [data-widget="image"] {
                        width: 500px !important;
                        height: auto !important;
                        max-width: 95% !important;
                        margin: 10px auto !important;
                        display: block !important;
                        box-sizing: border-box !important;
                    }
                    
                    img[data-cke-saved-src] {
                        width: 500px !important;
                        height: auto !important;
                        max-width: 95% !important;
                    }
                    
                    .cke_widget_wrapper, 
                    .cke_widget_element {
                        max-width: 95% !important;
                        margin: 10px auto !important;
                    }
                `;
                
                // 将CSS添加到style元素中
                if (styleElement.styleSheet) {
                    // IE的特殊处理
                    styleElement.styleSheet.cssText = cssRules;
                } else {
                    styleElement.appendChild(editorDocument.createTextNode(cssRules));
                }
                
                // 将style元素添加到iframe的head中
                editorDocument.head.appendChild(styleElement);
                
                console.log('Successfully injected CSS into CKEditor iframe');
            } catch (e) {
                console.error('Error injecting CSS into CKEditor:', e);
            }
            
            // 监听图片添加事件，限制图片尺寸
            editor.on('contentDom', function() {
                // 监听粘贴事件
                editor.document.on('paste', function(event) {
                    setTimeout(function() {
                        processImages(editor);
                    }, 100);
                });
                
                // 监听编辑器内容变化
                editor.document.on('keyup', function() {
                    processImages(editor);
                });
                
                // 初始处理已有图片
                processImages(editor);
            });
            
            // 监听对话框打开前事件，修改图片对话框默认行为
            editor.on('dialogShow', function(event) {
                var dialog = event.data;
                if (dialog.getName() === 'image' || dialog.getName() === 'image2') {
                    // 获取宽度输入框，设置默认值为500
                    var widthField = dialog.getContentElement('info', 'width') || 
                                      dialog.getContentElement('advanced', 'txtWidth');
                    if (widthField) {
                        widthField.setValue('500');
                    }
                    
                    // 尝试清除高度输入
                    var heightField = dialog.getContentElement('info', 'height') || 
                                       dialog.getContentElement('advanced', 'txtHeight');
                    if (heightField) {
                        heightField.setValue('');
                    }
                    
                    console.log('Image dialog opened, setting width=500px, height=auto');
                }
            });
            
            // 拦截并修改数据处理器
            editor.dataProcessor.htmlFilter.addRules({
                elements: {
                    img: function(element) {
                        // 强制设置宽度为500px，并删除高度
                        element.attributes.width = '500';
                        delete element.attributes.height;
                        return element;
                    }
                }
            });
        }
    };
    
    // 处理图片函数
    function processImages(editor) {
        const images = editor.document.find('img').toArray();
        
        images.forEach(function(img) {
            // 移除原有属性，应用新样式
            img.removeAttribute('width');
            img.removeAttribute('height');
            img.setStyle('width', '500px');
            img.setStyle('height', 'auto');
            img.setStyle('max-width', '95%');
            img.setStyle('margin', '10px auto');
            img.setStyle('display', 'block');
            
            // 如果图片是widget的一部分，尝试访问widget元素
            try {
                var widget = editor.widgets.getByElement(img);
                if (widget && widget.element) {
                    widget.element.removeAttribute('width');
                    widget.element.removeAttribute('height');
                }
            } catch (e) {
                console.log('Widget处理异常:', e);
            }
        });
    }
}; 

// 等待DOM加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 添加自定义样式到页面
    var style = document.createElement('style');
    style.type = 'text/css';
    style.innerHTML = `
        /* 确保CKEditor容器宽度一致 */
        .django-ckeditor-widget {
            width: 100% !important;
            display: block !important;
        }
        /* 确保编辑器UI与其他元素样式一致 */
        .cke_chrome {
            border-color: #ced4da !important;
            border-radius: 0.25rem !important;
            box-shadow: 0 .125rem .25rem rgba(0,0,0,.075) !important;
        }
        /* 调整编辑区域内边距 */
        .cke_contents {
            padding: 0.375rem 0.75rem !important;
        }
        /* 确保编辑器容器宽度一致 */
        .editor-container {
            width: 100% !important;
        }
        /* 调整CKEditor iframe宽度 */
        .cke_wysiwyg_frame, .cke_wysiwyg_div {
            width: 100% !important;
        }
        
        /* 覆盖CKEditor图片样式 */
        .cke_wysiwyg_frame {
            position: relative;
        }
        
        .cke_wysiwyg_frame::after {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 9999;
            pointer-events: none;
        }
        
        /* 尝试通过外部样式影响内部iframe */
        iframe.cke_wysiwyg_frame {
            width: 100% !important;
        }

        /* 隐藏最大化按钮 */
        .cke_button__maximize,
        .cke_button__maximize_icon,
        a[title*="maximize"],
        .cke_button[title*="Maximize"] {
            display: none !important;
        }
    `;
    document.getElementsByTagName('head')[0].appendChild(style);
    
    // 全局监听所有编辑器实例，这是为防止部分实例未被上面的配置捕获
    CKEDITOR.on('instanceReady', function(evt) {
        var editor = evt.editor;
        
        // 移除最大化按钮
        setTimeout(function() {
            try {
                // 使用jQuery查找并移除按钮（如果页面使用了jQuery）
                if (window.jQuery) {
                    jQuery('.cke_button__maximize, a[title*="maximize"], .cke_button[title*="Maximize"]').remove();
                }
                
                // 原生JS方式移除按钮
                document.querySelectorAll('.cke_button__maximize, a[title*="maximize"], .cke_button[title*="Maximize"]').forEach(function(el) {
                    el.parentNode.removeChild(el);
                });
                
                console.log('Maximize buttons removed from the DOM');
            } catch(e) {
                console.error('Error removing maximize buttons:', e);
            }
        }, 100);
        
        // 添加全局规则
        setTimeout(function() {
            try {
                // 直接添加DOM操作脚本到iframe
                var iframeDocument = editor.document.$;
                var script = iframeDocument.createElement('script');
                script.textContent = `
                    setInterval(function() {
                        var images = document.querySelectorAll('img');
                        for(var i=0; i<images.length; i++) {
                            var img = images[i];
                            img.style.width = '500px';
                            img.style.height = 'auto';
                            img.style.maxWidth = '95%';
                            img.style.margin = '10px auto';
                            img.style.display = 'block';
                            img.removeAttribute('width');
                            img.removeAttribute('height');
                        }
                    }, 1000);
                `;
                iframeDocument.body.appendChild(script);
            } catch(e) {
                console.error('Failed to inject script to iframe:', e);
            }
        }, 500);
    });
}); 