// Runs only after the original 3D initialization. Never rebuilds geometry.
// Existing records are mutated in place so click handlers retain live text.
export async function loadContent(original, lang, url) {
  window.__CONTENT_SOURCE__ = 'fallback';
  if(lang==='en')window.NEWS_DATA=[];
  try {
    const response = await fetch(url, {cache: 'no-cache'});
    if (!response.ok) return;
    const payload = await response.json();
    if (payload.lang !== lang || !Array.isArray(payload.units)) return;
    const sections = ['about', 'technology', 'pipeline', 'science', 'contact'];
    const publishedSections = Array.isArray(payload.sections) ? payload.sections.filter(s=>s&&typeof s.id==='string'&&/^[a-z][a-z0-9_-]{0,31}$/.test(s.id)&&typeof s.name==='string'&&s.name.trim()) : [];
    const sectionIds = [...new Set([...sections,...publishedSections.map(s=>s.id)])];
    const seen = new Set(), planned = [];
    for (const row of payload.units) {
      if (!row || typeof row.id !== 'string' || seen.has(row.id)) return;
      seen.add(row.id);
      const base = original.find(u => u.id === row.id);
      if (base) {
        // Source metadata and geometry always come from the embedded baseline.
        if (row.title !== undefined && (typeof row.title !== 'string' || !row.title.trim() || row.title.length > 200)) return;
        if (row.body !== undefined && (typeof row.body !== 'string' || row.body.length > 60000)) return;
        planned.push({...base, title: row.title ?? base.title, body: row.body ?? base.body});
      } else {
        if (!sectionIds.includes(row.sectionId) || !(sections.includes(row.sectionId) ? new RegExp(`^${sections.indexOf(row.sectionId)+1}-[1-9]\\d*$`) : /^[1-9]\d*-[1-9]\d*$/).test(row.id) || typeof row.title !== 'string' || !row.title.trim() || row.title.length>200 || typeof row.body !== 'string' || row.body.length>60000) return;
        planned.push({id: row.id, sectionId: row.sectionId, title: row.title, body: row.body});
      }
    }
    // News is an English baseline neuron even when older snapshots lack 1-6.
    if(lang==='en'&&!seen.has('1-6')){const news=original.find(u=>u.id==='1-6');if(news){planned.push(news);seen.add('1-6');}}
    if(lang==='en')window.NEWS_DATA=Array.isArray(payload.news)?payload.news.filter(n=>n&&typeof n.title==='string'&&typeof n.body==='string'):[];
    const control = window.__UNIT_CONTROL__;
    const visible = [];
    for (const row of planned) {
      const base = original.find(u => u.id === row.id);
      if (base) {Object.assign(base, {title:row.title, body:row.body}); visible.push(base);}
      else visible.push(row);
    }
    for (const unit of original) {
      const exists = seen.has(unit.id), button = control.buttons.get(unit.id);
      const article = document.querySelector(`#fallback-units [data-unit-id="${unit.id}"]`);
      if (button) {
        button.style.display = exists ? '' : 'none';
        button.setAttribute('aria-label', (lang === 'cn' ? '阅读' : 'Read ') + unit.title);
        button.querySelector('.unit-label').textContent = unit.title;
      }
      if (article) {
        article.hidden = !exists;
        article.querySelector('h2').textContent = unit.title;
        article.querySelector('p').textContent = unit.body;
      }
    }
    for (const row of visible.filter(u => !original.some(base => base.id === u.id))) {
      const article = document.createElement('article'), title = document.createElement('h2'), body = document.createElement('p');
      article.dataset.unitId = row.id; title.textContent = row.title; body.textContent = row.body;
      article.append(title, body); document.querySelector('#fallback-units').append(article);
    }
    // Extra copy uses a small reading list, including on narrow screens. This
    // deliberately adds no new 3D neurons to the approved scene.
    const extras = visible.filter(u => sections.includes(u.sectionId) && !original.some(base => base.id === u.id));
    if (extras.length) {
      const region = document.createElement('aside');
      region.className = 'cms-extra-units';
      region.setAttribute('aria-label', lang === 'cn' ? '新增内容' : 'Additional content');
      region.style.cssText = 'position:fixed;z-index:4;right:6vw;max-width:220px;max-height:32vh;overflow-y:auto;display:grid;gap:8px';
      const buttons = extras.map(unit => {
        const button = document.createElement('button');
        button.type = 'button'; button.dataset.unitId = unit.id; button.textContent = unit.title;
        button.style.cssText = 'color:#d5e9dc;background:#071713e8;border:1px solid #2de06a66;padding:10px 14px;border-radius:6px;font:inherit;text-align:left;cursor:pointer';
        button.onclick = () => control.open(unit.title, unit.body, button, unit.id);
        region.append(button); return {button, unit};
      });
      document.body.append(region);
      const update = () => {
        region.style.bottom = matchMedia('(max-width:700px)').matches ? '220px' : '110px';
        const active = sections[window.__NET_STATS__?.activeCluster || 0];
        region.hidden = document.body.classList.contains('footer-visible') || document.querySelector('#info-dialog').classList.contains('open');
        // inline display must be cleared for the native hidden attribute.
        region.style.display = region.hidden ? 'none' : 'grid';
        buttons.forEach(({button, unit}) => button.hidden = unit.sectionId !== active);
      };
      addEventListener('scroll', update, {passive:true});
      addEventListener('resize', update, {passive:true});
      new MutationObserver(update).observe(document.querySelector('#info-dialog'), {attributes:true,attributeFilter:['class']});
      new MutationObserver(update).observe(document.querySelector('#section-float'), {attributes:true,attributeFilter:['data-active-cluster']});
      update();
    }
    document.querySelectorAll('.section-float-copy').forEach(copy => {
      const list = copy.querySelector('.section-float-units'); list.replaceChildren();
      visible.filter(u => u.sectionId === copy.dataset.sectionId).forEach(unit => {
        const item = document.createElement('li');
        const button = document.createElement('button');
        button.type = 'button'; button.textContent = unit.title;
        button.dataset.unitId = unit.id;
        button.setAttribute('aria-label', '阅读' + unit.title);
        button.style.cssText = 'pointer-events:auto;color:inherit;font:inherit;background:none;border:0;padding:2px 0;cursor:pointer;text-align:left';
        button.onclick = () => control.open(unit.title, unit.body, button, unit.id);
        item.append(button);
        list.append(item);
      });
    });
    for(const s of publishedSections.filter(s=>!sections.includes(s.id))){
      const region=document.createElement('section'),heading=document.createElement('h2');
      region.id='cms-column-'+s.id;region.className='cms-column';
      region.style.cssText='position:relative;z-index:2;margin:40px 6vw;padding:28px;background:#081a20;border:1px solid #2de06a66;border-radius:12px;scroll-margin-top:160px';
      heading.textContent=s.name;region.append(heading);
      for(const u of visible.filter(u=>u.sectionId===s.id)){const article=document.createElement('article'),title=document.createElement('h3'),body=document.createElement('p');title.textContent=u.title;body.textContent=u.body;body.style.whiteSpace='pre-line';article.append(title,body);region.append(article);}
      document.querySelector('.footer').before(region);
    }
    window.applyCmsTexts(payload.texts, publishedSections, lang);
    window.CONTENT_UNITS = visible;
    window.__CONTENT_SOURCE__ = 'cms';
    window.__CONTENT_GENERATED_AT__ = payload.generatedAt || null;
    window.dispatchEvent(new CustomEvent('cms-content-ready'));
  } catch {window.__CONTENT_SOURCE__ = 'fallback';}
}
