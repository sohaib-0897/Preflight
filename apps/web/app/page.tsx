import Script from 'next/script';
export default function Home(){
 return <><div id="app"/><Script src="/app.js" type="module" strategy="afterInteractive"/></>;
}
