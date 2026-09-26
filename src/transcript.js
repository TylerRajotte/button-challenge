import './transcript.css';
import {marked} from 'marked';
import DOMPurify from 'dompurify';
import {asset} from './urls.js';
const host=document.querySelector('#messages');
try{
  const response=await fetch(asset('transcript.json'));
  if(!response.ok)throw new Error('Transcript unavailable');
  const {messages}=await response.json();host.replaceChildren();
  document.querySelector('#message-count').textContent=`iPad · T3 Code · Started at ${messages[0].time}`;
  for(const [i,message] of messages.entries()){
    const article=document.createElement('article');article.className=`message ${message.role}`;article.id=`message-${i+1}`;
    const heading=document.createElement('h2');heading.textContent=message.role==='user'?'User':'Codex';
    const number=document.createElement('a');number.href=`#${article.id}`;number.textContent=`#${i+1}`;number.setAttribute('aria-label',`Link to message ${i+1}`);const time=document.createElement('time');time.dateTime=message.timestamp;time.textContent=message.time;time.title=`${message.date}, ${message.time} · original session local time`;heading.append(time,number);
    const body=document.createElement('div');body.className='message-body';
    const markdown=message.text.replace(/\[([^\]]+)\]\(\[private development address redacted\]\)/g,'$1 ([private development address redacted])');
    body.innerHTML=DOMPurify.sanitize(marked.parse(markdown),{ALLOWED_TAGS:['p','br','strong','em','del','a','ul','ol','li','blockquote','pre','code','h1','h2','h3','h4','hr','table','thead','tbody','tr','th','td'],ALLOWED_ATTR:['href','title']});
    for(const link of body.querySelectorAll('a')){if(!/^https?:\/\//i.test(link.getAttribute('href')??'')){link.replaceWith(document.createTextNode(link.textContent));}else{link.target='_blank';link.rel='noopener noreferrer';}}
    article.append(heading,body);host.append(article);
  }
}catch{host.textContent='The conversation could not load. Please refresh the page.';}
