import argparse, json
from app.core.schemas import SessionCreate, GenerateRequest
from app.core.session_manager import SessionManager
from app.core.enums import Provider, SafetyProfile
from app.core.provider_router import ProviderRouter
from app.providers.openai_adapter import OpenAIImageAdapter
from app.providers.gemini_adapter import GeminiImageAdapter
from app.services.image_service import ImageService
from app.storage.db import SessionLocal, init_db
from app.storage.repositories import Repository

def main():
    init_db(); p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    cs=sub.add_parser('create-session'); cs.add_argument('--provider',choices=['openai','gemini'],required=True); cs.add_argument('--model'); cs.add_argument('--safety',default='balanced')
    gen=sub.add_parser('generate'); gen.add_argument('session_id'); gen.add_argument('prompt'); gen.add_argument('--fallback-provider',choices=['openai','gemini'])
    hist=sub.add_parser('history'); hist.add_argument('session_id')
    la=sub.add_parser('list-assets'); la.add_argument('session_id')
    args=p.parse_args(); db=SessionLocal(); repo=Repository(db)
    try:
        if args.cmd=='create-session': print(json.dumps({'session_id':SessionManager(repo).create(SessionCreate(provider=Provider(args.provider),model=args.model,default_safety_profile=SafetyProfile(args.safety))).session_id}))
        elif args.cmd=='generate':
            router=ProviderRouter({Provider.openai:OpenAIImageAdapter(),Provider.gemini:GeminiImageAdapter()}, True)
            turn,assets,provider,fb,orig=ImageService(repo,router).generate(args.session_id,GenerateRequest(prompt=args.prompt,fallback_provider=Provider(args.fallback_provider) if args.fallback_provider else None))
            print(json.dumps({'turn_id':turn.turn_id,'provider':provider,'assets':[a.asset_id for a in assets],'fallback':fb,'original_error':orig},default=str))
        elif args.cmd=='history': print(json.dumps([t.__dict__ for t in repo.list_turns(args.session_id)],default=str))
        elif args.cmd=='list-assets': print(json.dumps([a.__dict__ for a in repo.list_assets(args.session_id)],default=str))
    finally: db.close()
if __name__=='__main__': main()
