import Platform from '../../components/platform';
export default async function Module({params}:{params:Promise<{slug:string[]}>}) { const {slug}=await params; return <Platform slug={slug}/>; }
