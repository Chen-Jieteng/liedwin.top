/**
 * 目录生成器 - 基于文章中的标题自动生成目录
 */
function generateTOC(contentSelector, tocSelector) {
    // 获取内容区域和目录容器
    const content = document.querySelector(contentSelector);
    const toc = document.querySelector(tocSelector);
    
    if (!content || !toc) return;
    
    // 清空现有目录
    toc.innerHTML = '';
    
    // 查找所有标题元素
    const headings = content.querySelectorAll('h1, h2, h3, h4, h5, h6');
    
    if (headings.length === 0) {
        toc.innerHTML = '<div class="text-muted text-center py-3">文章未包含目录</div>';
        return;
    }
    
    // 创建目录列表
    const tocList = document.createElement('ul');
    tocList.className = 'list-unstyled mb-0';
    
    // 为每个标题创建ID和目录项
    headings.forEach((heading, index) => {
        // 为没有ID的标题创建一个唯一ID
        if (!heading.id) {
            heading.id = `heading-${index}`;
        }
        
        // 创建目录项
        const listItem = document.createElement('li');
        
        // 根据标题级别添加缩进
        const headingLevel = parseInt(heading.tagName.substring(1));
        listItem.classList.add(`ml-${(headingLevel-1)*2}`);
        
        // 创建链接
        const link = document.createElement('a');
        link.href = `#${heading.id}`;
        link.className = 'toc-link d-block py-1';
        link.textContent = heading.textContent;
        
        // 为比较小的标题添加更小的字体和浅色
        if (headingLevel > 2) {
            link.classList.add('small');
            if (headingLevel > 3) {
                link.classList.add('text-muted');
            }
        }
        
        listItem.appendChild(link);
        tocList.appendChild(listItem);
    });
    
    // 添加目录到容器
    toc.appendChild(tocList);
}

// 页面加载完成后生成目录
document.addEventListener('DOMContentLoaded', function() {
    // 延迟一点执行以确保内容已经加载
    setTimeout(function() {
        generateTOC('.article-content', '#toc-container');
    }, 100);
}); 