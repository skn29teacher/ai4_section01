"use strict";
const root = document.getElementById("app");
let user = null, csrf = "";
const esc = value => String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const pageParam = () => new URLSearchParams(location.search).get("page") || "1";
const errorBox = () => '<p class="error" id="error" role="alert"></p>';
const field = (key, label, type="text", max=254, value="") => `<div class="field"><label for="${key}">${label}</label><input id="${key}" name="${key}" type="${type}" maxlength="${max}" value="${esc(value)}" required ${type === "password" ? 'autocomplete="current-password"' : ""}></div>`;
function showError(error){ const box=document.getElementById("error"); if(box) box.textContent=error.message; }
async function api(path, method="GET", data){
  const response=await fetch("/api"+path,{method,credentials:"same-origin",headers:{"Content-Type":"application/json","X-CSRF-Token":csrf},body:data===undefined?undefined:JSON.stringify(data)});
  let result; try{result=await response.json();}catch{throw new Error("서버 응답을 확인할 수 없습니다. 잠시 후 다시 시도하세요.");}
  if(!response.ok){const error=new Error(result.error||"요청을 처리할 수 없습니다.");error.status=response.status;throw error;}
  if(result.csrf_token) csrf=result.csrf_token;
  return result;
}
function bindForm(id, submit){
  const form=document.getElementById(id);
  form.addEventListener("submit",async event=>{
    event.preventDefault(); const button=form.querySelector('[type="submit"]');button.disabled=true;
    const box=document.getElementById("error");if(box)box.textContent="";
    try{await submit(Object.fromEntries(new FormData(form)));}catch(error){showError(error);}finally{button.disabled=false;}
  });
}
function requireUser(){if(!user){location.replace("/login");return false;}return true;}
function nav(){
  document.getElementById("nav").innerHTML=user?`${user.role==="ADMIN"?'<a href="/admin/mask-rules">표현 관리</a>':""}<span>${esc(user.nickname)}</span><button class="secondary" id="logout">로그아웃</button>`:'<a href="/login">로그인</a><a href="/signup">회원가입</a>';
  document.getElementById("logout")?.addEventListener("click",async()=>{try{await api("/auth/logout","POST",{});location.assign("/");}catch(error){alert(error.message);}});
}
async function list(){
  const result=await api("/posts?page="+encodeURIComponent(pageParam()));
  history.replaceState(null,"",result.page===1?"/":"/?page="+result.page);
  root.innerHTML=`<div class="toolbar"><div><p class="eyebrow">YOUR EVERYDAY NOTES</p><h1>작은 기록들</h1><p class="muted">생각을 남기고, 이야기를 나누세요.</p></div><a class="button" href="${user?"/posts/new":"/login"}">글쓰기</a></div>${result.items.length?`<ul class="post-list">${result.items.map(p=>`<li><a href="/posts/${p.id}?page=${result.page}"><span class="post-title">${esc(p.title)}</span>${p.is_mine?'<span class="my-post-badge">내 글</span>':""}</a></li>`).join("")}</ul>`:'<p class="empty">아직 기록이 없습니다. 첫 글을 남겨보세요.</p>'}<div class="pagination">${result.page>1?`<a class="button secondary" href="/?page=${result.page-1}">이전</a>`:""}<span>${result.page} / ${result.pages}</span>${result.page<result.pages?`<a class="button secondary" href="/?page=${result.page+1}">다음</a>`:""}</div>`;
}
function authScreen(kind){
  const signup=kind==="signup",forgot=kind==="forgot-password";
  const title=signup?"회원가입":forgot?"비밀번호 찾기":"로그인";
  root.innerHTML=`<section class="card auth"><p class="eyebrow">NOTE · DEMO</p><h1>${title}</h1>${forgot?'<p class="notice">목업 화면입니다. 실제 메일을 발송하거나 비밀번호를 변경하지 않습니다.</p>':'<p class="muted">데모 서비스입니다. 실사용 비밀번호를 입력하지 마세요.</p>'}<form id="auth-form">${field("email","이메일","email")}${signup?field("nickname","닉네임","text",50):""}${!forgot?field("password","비밀번호","password",128):""}${!forgot?'<p class="muted">가입 비밀번호는 8~128자입니다.</p>':""}${errorBox()}<div class="actions"><button type="submit">${title}</button></div></form><div class="links"><a href="/login">로그인</a><a href="/signup">회원가입</a><a href="/forgot-password">비밀번호 찾기</a></div></section>`;
  if(signup)document.getElementById("password").autocomplete="new-password";
  bindForm("auth-form",async data=>{
    const result=await api("/auth/"+kind,"POST",data);
    if(forgot){document.getElementById("error").className="notice";document.getElementById("error").textContent=result.message;}
    else if(signup){location.assign("/login?registered=1");}else location.assign("/");
  });
  if(kind==="login"&&new URLSearchParams(location.search).has("registered")){document.getElementById("error").className="notice";document.getElementById("error").textContent="가입이 완료되었습니다. 로그인하세요.";}
}
async function editor(id){
  if(!requireUser())return;
  const post=id?(await api(`/posts/${id}/edit`)).post:{title:"",content:""};
  root.innerHTML=`<p class="eyebrow">WRITE A NOTE</p><h1>${id?"기록 수정":"새로운 기록"}</h1><form id="post-form" class="card">${field("title","제목","text",200,post.title)}<div class="field"><label for="content">내용</label><textarea id="content" name="content" maxlength="10000" rows="12" required>${esc(post.content)}</textarea></div>${errorBox()}<div class="actions"><button type="submit">저장</button><a class="button secondary" href="${id?`/posts/${id}`:"/"}">취소</a></div></form>`;
  bindForm("post-form",async data=>{const result=await api(id?`/posts/${id}`:"/posts",id?"PATCH":"POST",data);location.assign(`/posts/${id||result.id}`);});
}
async function commentList(id){
  const result=await api(`/posts/${id}/comments`);
  document.getElementById("comments").innerHTML=result.items.length?result.items.map(c=>`<div class="comment"><div class="comment-author"><small>${esc(c.nickname)}</small>${c.is_mine?'<span class="my-post-badge">내 댓글</span>':""}</div><p>${esc(c.content)}</p></div>`).join(""):'<p class="muted">아직 댓글이 없습니다.</p>';
}
async function detail(id){
  const {post}=await api(`/posts/${id}`);
  root.innerHTML=`<p class="eyebrow">A SMALL NOTE</p><h1 class="detail-title">${esc(post.title)}</h1><div class="body-text">${esc(post.content)}</div><div class="actions"><a class="button secondary" href="/?page=${encodeURIComponent(pageParam())}">목록</a>${post.can_edit?`<a class="button secondary" href="/posts/${id}/edit">수정</a><button class="danger" id="delete">삭제</button>`:""}</div><hr><h2>댓글</h2><div id="comments"></div>${user?`<form id="comment-form" class="comment-form"><label for="content">댓글 남기기</label><textarea id="content" name="content" maxlength="2000" required></textarea>${errorBox()}<div class="actions"><button type="submit">등록</button></div></form>`:'<p class="notice"><a href="/login">로그인</a> 후 댓글을 남길 수 있습니다.</p>'}`;
  document.getElementById("delete")?.addEventListener("click",async()=>{if(confirm("이 글과 연결된 댓글을 삭제할까요?")){try{await api(`/posts/${id}`,"DELETE");location.assign("/?page="+encodeURIComponent(pageParam()));}catch(error){alert(error.message);}}});
  await commentList(id);
  if(user)bindForm("comment-form",async data=>{await api(`/posts/${id}/comments`,"POST",data);await commentList(id);document.getElementById("content").value="";});
}
async function admin(){
  if(!requireUser())return;
  if(user.role!=="ADMIN")throw new Error("관리자만 이용할 수 있습니다.");
  const result=await api("/admin/mask-rules");
  root.innerHTML=`<p class="eyebrow">ADMINISTRATION</p><h1>표현 사전 관리</h1><p class="muted">등록한 키워드는 게시글 제목·본문·댓글에서 마스킹됩니다.</p><p class="notice">규칙을 삭제하면 기존 글의 원문 표현이 다시 표시될 수 있습니다.</p><form id="rule-form" class="rule-form"><label for="expression">새 표현</label><input id="expression" name="expression" maxlength="255" required>${errorBox()}<div class="actions"><button type="submit">추가</button></div></form><ul class="rule-list">${result.items.map(r=>`<li><span>${esc(r.expression)}</span><button class="danger" data-rule-id="${r.id}">삭제</button></li>`).join("")}</ul>${!result.items.length?'<p class="empty">등록된 표현이 없습니다.</p>':""}`;
  bindForm("rule-form",async data=>{await api("/admin/mask-rules","POST",data);await admin();});
  root.querySelectorAll("[data-rule-id]").forEach(button=>button.addEventListener("click",async()=>{if(confirm("이 규칙을 삭제할까요? 원문 표현이 다시 표시될 수 있습니다.")){try{await api("/admin/mask-rules/"+button.dataset.ruleId,"DELETE");await admin();}catch(error){showError(error);}}}));
}
async function start(){
  try{
    const auth=await api("/auth/me");user=auth.user;nav();
    const path=location.pathname,match=path.match(/^\/posts\/(\d+)(\/edit)?$/);
    if(path==="/")await list();
    else if(["/signup","/login","/forgot-password"].includes(path))authScreen(path.slice(1));
    else if(path==="/posts/new")await editor();
    else if(match)await(match[2]?editor(match[1]):detail(match[1]));
    else if(path==="/admin/mask-rules")await admin();
    else throw new Error("존재하지 않는 페이지입니다.");
  }catch(error){root.innerHTML=`<section class="card"><h1>안내</h1><p class="error">${esc(error.message)}</p><a class="button secondary" href="/">목록으로</a></section>`;}
}
start();
