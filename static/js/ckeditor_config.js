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
    
    // 添加格式化选项，支持标题
    config.format_tags = 'p;h1;h2;h3;h4;h5;h6;pre';
    
    // 添加CSRF令牌到上传请求
    config.extraPlugins = 'uploadimage,clipboard,dialogadvtab,image2';
    
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
        { name: 'tools', items: ['Maximize', 'ShowBlocks'] }
    ];
    
    // 设置编辑器宽度与其他表单元素保持一致
    config.width = '100%';
    config.height = '400px';
    
    // 图片上传前添加CSRF令牌
    config.on = {
        instanceReady: function(evt) {
            const editor = evt.editor;
            
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
        }
    };
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
    `;
    document.getElementsByTagName('head')[0].appendChild(style);
}); 