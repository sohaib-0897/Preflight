import type { ReactNode } from 'react';
import '@fontsource/inter/400.css';
import '@fontsource/inter/500.css';
import '@fontsource/inter/600.css';
import '@fontsource/jetbrains-mono/400.css';
import './globals.css';
export const metadata = {title:'Preflight · Agent evaluation',description:'Evidence-backed agent evaluation and release decisions'};
export default function RootLayout({children}:{children:ReactNode}) {return <html lang="en"><body><a className="skip" href="#main">Skip to content</a>{children}</body></html>;}
