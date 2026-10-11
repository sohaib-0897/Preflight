const origin=process.env.PREFLIGHT_API_ORIGIN??'http://127.0.0.1:8000';
export default {
 output:'standalone',
 poweredByHeader:false,
 turbopack:{root:process.cwd()},
 async rewrites(){return [{source:'/api/:path*',destination:`${origin}/api/:path*`},{source:'/docs',destination:`${origin}/docs`},{source:'/openapi.json',destination:`${origin}/openapi.json`}];},
};
