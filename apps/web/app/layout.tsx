import type { ReactNode } from 'react';
import './globals.css';
export const metadata = {title:'Preflight · Agent evaluation',description:'Evidence-based local agent evaluation'};
export default function RootLayout({children}:{children:ReactNode}) {
 return <html lang="en"><body><a className="skip" href="#main">Skip to content</a>{children}<div id="announcement" role="status" aria-live="polite"/><dialog id="dialog" aria-labelledby="dialog-title"/></body></html>;
}
