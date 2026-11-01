#!/usr/bin/env python3
import json, time, urllib.request
import websocket

tabs = json.load(urllib.request.urlopen("http://127.0.0.1:18801/json", timeout=10))
page = next(t for t in tabs if t["type"] == "page")
ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=150, suppress_origin=True)
mid = 0
def send(method, params=None):
    global mid
    mid += 1
    ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == mid:
            return m.get("result", {})
def js(expr):
    r = send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True})
    if "exceptionDetails" in r:
        return "EXC:" + json.dumps(r["exceptionDetails"].get("exception", {}).get("description", ""))[:120]
    return r.get("result", {}).get("value")

def setf(name, value):
    return js("""(function(){
      var el = document.querySelector('[name="%s"]');
      if (!el) return 'NO %s';
      var proto = el.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto, 'value').set.call(el, %s);
      el.dispatchEvent(new Event('input', {bubbles: true}));
      el.dispatchEvent(new Event('change', {bubbles: true}));
      return 'ok';
    })()""" % (name, name, json.dumps(value)))

print(setf("name", "CROX Sec"))
print(setf("description", "Security research team — OSINT, passive external audits, web, forensics. https://croxsec.com"))
# country -> ES
print(js("var s=document.querySelector('select[name=country]'); if(!s) 'NO country'; else { s.value='ES'; s.dispatchEvent(new Event('change',{bubbles:true})); 'ES ok: '+s.value }"))
time.sleep(1)
# ejecutar reCAPTCHA explicitamente y esperar token
print(js("""(function(){
  var w = document.querySelector('.g-recaptcha');
  var sitekey = w ? w.getAttribute('data-sitekey') : null;
  if (!sitekey) return 'NO sitekey';
  return new Promise(function(res){
    grecaptcha.ready(function(){
      grecaptcha.execute(sitekey, {action: 'submit'}).then(function(t){
        var ta = document.querySelector('textarea[name="g-recaptcha-response"]');
        if (ta) { ta.value = t; ta.dispatchEvent(new Event('input',{bubbles:true})); }
        res('token len ' + t.length);
      }).catch(function(e){ res('exec fail: ' + e); });
    });
  });
})()"""))
time.sleep(1.5)
print("token field:", js("(document.querySelector('textarea[name=\"g-recaptcha-response\"]')||{value:''}).value.length"))
print(js("var b=document.querySelector('[type=submit]'); b?(b.click(),'SUBMIT'):'NO BTN'"))
time.sleep(8)
print("url:", js("location.href"))
print("errores:", js("Array.from(document.querySelectorAll('.errorlist li, .text-danger, [role=alert]')).map(e=>(e.innerText||'').trim()).filter(Boolean).slice(0,5).join(' | ')"))
ws.close()
