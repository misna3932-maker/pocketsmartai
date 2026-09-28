document.addEventListener('DOMContentLoaded',()=>{
 const input=document.querySelector('[data-outfit-input]'), preview=document.querySelector('[data-outfit-preview]'), remove=document.querySelector('[data-remove-image]');
 if(input){input.addEventListener('change',()=>{const f=input.files?.[0];if(!f)return;if(!f.type.startsWith('image/')){alert('Please select an image file.');input.value='';return;}const r=new FileReader();r.onload=e=>{preview.src=e.target.result;preview.style.display='block';remove.hidden=false};r.readAsDataURL(f);});}
 if(remove){remove.addEventListener('click',()=>{input.value='';preview.src='';preview.style.display='none';remove.hidden=true;});}
});
function printPage(){window.print()}
