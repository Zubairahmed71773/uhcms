(function(){
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
function toast(m,t){const b=$('#toasts');if(!b)return;const e=document.createElement('div');e.className='toast '+(t||'');e.setAttribute('role','status');e.textContent=m;b.appendChild(e);setTimeout(()=>e.remove(),4500)}
window.toast=toast;
$$('[data-flash]').forEach(e=>toast(e.textContent.trim()));
$$('[data-toggle-pw]').forEach(b=>b.addEventListener('click',()=>{const i=$('#'+b.dataset.togglePw);const s=i.type==='password';i.type=s?'text':'password';b.textContent=s?'Hide':'Show';b.setAttribute('aria-pressed',s)}));
$$('form[data-validate]').forEach(f=>f.addEventListener('submit',e=>{let bad=false;
$$('[data-min]',f).forEach(i=>{const m=$('.err',i.parentElement.parentElement)||$('.err',i.parentElement);const short=i.value.length<+i.dataset.min;if(m)m.textContent=short?'Use at least '+i.dataset.min+' characters.':'';bad=bad||short});
if(bad){e.preventDefault();toast('Please fix the highlighted fields.','bad')}}));
const io=new IntersectionObserver(es=>es.forEach(x=>{if(!x.isIntersecting)return;io.unobserve(x.target);const el=x.target,end=+el.dataset.count;let n=0;const st=Math.max(1,Math.ceil(end/40));const t=setInterval(()=>{n=Math.min(end,n+st);el.textContent=n+(el.dataset.suffix||'');if(n>=end)clearInterval(t)},30)}));
$$('[data-count]').forEach(e=>io.observe(e));
const rv=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');rv.unobserve(x.target)}}));
$$('.reveal').forEach(e=>rv.observe(e));
$$('[data-drop]').forEach(b=>{const p=$('#'+b.dataset.drop);b.addEventListener('click',e=>{e.stopPropagation();p.classList.toggle('open');b.setAttribute('aria-expanded',p.classList.contains('open'))});p.addEventListener('click',e=>e.stopPropagation())});
document.addEventListener('click',()=>$$('.drop.open').forEach(d=>d.classList.remove('open')));
$$('[data-modal]').forEach(b=>b.addEventListener('click',()=>$('#'+b.dataset.modal).showModal()));
$$('[data-close]').forEach(b=>b.addEventListener('click',()=>b.closest('dialog').close()));
const cf=$('#contactform');if(cf)cf.addEventListener('submit',e=>{e.preventDefault();cf.reset();toast('Thanks! Your message was recorded (demo form).','ok')});
})();
