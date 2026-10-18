import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sixth.main import create_app
from sixth.models import Intent
from sixth.planner import Planner
from test_accounts import (  # noqa: F401
    account_settings,  # noqa: F401
    google,
    login,
)
from test_application import approve, send, wait


def post(client, headers, path, body=None, key=None):
    return client.post(path, headers={**headers, 'Idempotency-Key': key or uuid.uuid4().hex}, json=body)


@pytest.fixture
def people(request):
    configuration = request.getfixturevalue("google")
    app = create_app(configuration)
    with TestClient(app) as a:
        b, c = TestClient(app), TestClient(app)
        ah, bh, ch = login(a, 'avery'), login(b, 'jules'), login(c, 'outsider')
        au, bu = a.get('/v1/friends').json()['username'], b.get('/v1/friends').json()['username']
        friend = a.post('/v1/friends', headers=ah, json={'username': bu}).json()['id']
        assert b.post(f'/v1/friends/{friend}/accept', headers=bh).status_code == 200
        start = (datetime.now(timezone.utc) + timedelta(days=2)).replace(hour=7, minute=30, second=0, microsecond=0)
        body = {'title': 'Private meeting title', 'starts_at': start.isoformat(), 'ends_at': (start+timedelta(hours=2)).isoformat(), 'timezone': 'Asia/Calcutta'}
        yield a, b, c, ah, bh, ch, au, bu, friend, body
        b.close()
        c.close()


def test_private_availability_sharing_and_boundary(people):
    a,b,c,ah,bh,ch,au,bu,friend,body = people
    assert post(a,ah,'/v1/calendar/events',body).status_code == 201
    query = {key:body[key] for key in ('starts_at','ends_at','timezone')}
    path = f'/v1/friends/{friend}/availability'
    assert b.get(path,params=query).json()['status'] == 'unknown'
    assert a.put(f'/v1/friends/{friend}/sharing',headers=ah,json={'availability':True}).status_code == 200
    result = b.get(path,params=query).json()
    assert result['status'] == 'busy' and len(result['busy']) == 1
    assert body['title'] not in str(result)
    assert c.get(path,params=query).status_code == 409
    query.update(starts_at=body['ends_at'],ends_at=(datetime.fromisoformat(body['ends_at'])+timedelta(hours=1)).isoformat())
    assert b.get(path,params=query).json()['status'] == 'no_recorded_conflict'
    assert b.get('/v1/calendar/events').json()['items'] == []
    assert a.put(f'/v1/friends/{friend}/sharing',headers=ah,json={'availability':False}).status_code == 200
    assert b.get(path,params=query).json()['status'] == 'unknown'


def test_meeting_acceptance_confirmation_cancellation_replay(people):
    a,b,c,ah,bh,ch,au,bu,friend,body = people
    request = post(a,ah,'/v1/scheduling/meeting',{**body,'friend_usernames':[bu]},'invitation-once')
    assert request.status_code == 201, request.text
    item = request.json()
    identifier=item['id']
    assert post(a,ah,'/v1/scheduling/meeting',{**body,'friend_usernames':[bu]},'invitation-once').json()['id'] == identifier
    assert b.get('/v1/scheduling/inbox').json()['items'][0]['id'] == identifier
    assert c.get('/v1/scheduling/inbox').json()['items'] == []
    assert post(a,ah,f'/v1/scheduling/meeting/{identifier}/confirm').status_code == 409
    assert post(a,ah,f'/v1/scheduling/meeting/{identifier}/respond',{'accepted':True}).status_code == 409
    assert post(c,ch,f'/v1/scheduling/meeting/{identifier}/respond',{'accepted':True}).status_code == 409
    assert post(b,bh,f'/v1/scheduling/meeting/{identifier}/respond',{'accepted':True}).json()['status'] == 'ready_to_book'
    assert a.get('/v1/calendar/events').json()['items'] == []
    assert post(a,ah,f'/v1/scheduling/meeting/{identifier}/confirm').json()['status'] == 'booked'
    assert post(a,ah,f'/v1/scheduling/meeting/{identifier}/confirm').json()['status'] == 'booked'
    for client in (a,b):
        assert len(client.get('/v1/calendar/events').json()['items']) == 1
    assert post(a,ah,f'/v1/scheduling/meeting/{identifier}/cancel').json()['status'] == 'cancelled'
    for client in (a,b):
        assert client.get('/v1/calendar/events').json()['items'] == []


def test_conflict_rechecked_without_partial_booking(people):
    a,b,c,ah,bh,ch,au,bu,friend,body = people
    identifier = post(a,ah,'/v1/scheduling/meeting',{**body,'friend_usernames':[bu]}).json()['id']
    post(b,bh,f'/v1/scheduling/meeting/{identifier}/respond',{'accepted':True})
    assert post(b,bh,'/v1/calendar/events',body).status_code == 201
    assert post(a,ah,f'/v1/scheduling/meeting/{identifier}/confirm').status_code == 409
    assert a.get('/v1/calendar/events').json()['items'] == []
    assert len(b.get('/v1/calendar/events').json()['items']) == 1


def test_one_time_question_does_not_share_or_book(people):
    a,b,c,ah,bh,ch,au,bu,friend,body = people
    identifier = post(a,ah,'/v1/scheduling/availability_request',{**body,'friend_usernames':[bu]}).json()['id']
    response = post(b,bh,f'/v1/scheduling/availability_request/{identifier}/respond',{'accepted':True})
    assert response.json()['status'] == 'answered'
    assert a.get('/v1/calendar/events').json()['items'] == []
    assert b.get(f'/v1/friends/{friend}/context').json()['availability_shared'] is False


def test_presence_expiry_and_invalid_times(people):
    a,b,c,ah,bh,ch,au,bu,friend,body = people
    assert a.get('/v1/availability').json()['status'] == 'unknown'
    assert a.put('/v1/availability',headers=ah,json={'status':'busy','until':'2020-01-01T00:00:00Z'}).status_code == 422
    future=(datetime.now(timezone.utc)+timedelta(hours=2)).isoformat()
    assert a.put('/v1/availability',headers=ah,json={'status':'busy','until':future}).status_code == 200
    assert a.get('/v1/availability').json()['status'] == 'busy'
    owner=a.get('/v1/session').json()['account']
    a.app.state.store.put(owner,'presence',{'id':'self','status':'busy','until':'2020-01-01T00:00:00Z'})
    assert a.get('/v1/availability').json()['status'] == 'unknown'
    for bad in ({**body,'ends_at':body['starts_at']},{**body,'starts_at':'2028-01-01T13:00:00'},{**body,'timezone':'invalid'}):
        assert post(a,ah,'/v1/calendar/events',bad).status_code == 409


def test_explicit_memory_sharing_revoke_and_unfriend(people):
    a,b,c,ah,bh,ch,au,bu,friend,body = people
    task,_=send(a,ah,'I am vegetarian')
    fact=task['evidence'][0]
    assert b.get(f'/v1/friends/{friend}/context').json()['memories'] == []
    assert a.put(f'/v1/friends/{friend}/sharing',headers=ah,json={'memory_ids':[fact['id']]}).status_code == 200
    shared=b.get(f'/v1/friends/{friend}/context').json()['memories']
    assert shared[0]['value']=='vegetarian' and 'sources' not in shared[0]
    assert b.get('/v1/memory').json()['items'] == []
    assert a.delete(f"/v1/memory/{fact['id']}",headers=ah).status_code == 202
    assert b.get(f'/v1/friends/{friend}/context').json()['memories'] == []
    assert a.delete(f'/v1/friends/{friend}',headers=ah).status_code == 200
    assert b.get(f'/v1/friends/{friend}/context').status_code == 404


def test_ai_proposal_needs_approval_and_uses_own_context(people,monkeypatch):
    a,b,c,ah,bh,ch,au,bu,friend,body = people
    contexts=[]
    def parse(self,text,**kwargs):
        contexts.append(kwargs['scheduling_context'])
        return Intent(kind='scheduling',schedule_action='propose_meeting',friend_usernames=[bu],meeting_title='Tea',starts_at=body['starts_at'],ends_at=body['ends_at'])
    monkeypatch.setattr(Planner,'parse',parse)
    task,_=send(a,ah,'Invite Jules for tea')
    assert task['status']=='awaiting_input' and task['action']['tool']=='scheduling.apply'
    assert a.get('/v1/scheduling/inbox').json()['items']==[]
    assert contexts[0]['friends'][0]['username']==bu
    invalid={key:task['action'][key] for key in ('decision_id','fingerprint','plan_revision')}
    invalid.update(decision='approve',fingerprint='wrong')
    assert post(a,ah,f"/v1/tasks/{task['id']}/decisions",invalid).status_code == 409
    assert approve(a,ah,task).status_code==202
    assert wait(a,task['id'])['result']['status']=='succeeded'
    assert len(b.get('/v1/scheduling/inbox').json()['items'])==1
    assert a.get('/v1/calendar/events').json()['items']==[]


def test_blocking_profile_flag_and_removed_friend_prevent_booking(people):
    a,b,c,ah,bh,ch,au,bu,friend,body = people
    identifier=post(a,ah,'/v1/scheduling/meeting',{**body,'friend_usernames':[bu]}).json()['id']
    post(b,bh,f'/v1/scheduling/meeting/{identifier}/respond',{'accepted':True})
    assert b.put('/v1/availability',headers=bh,json={'status':'away'}).status_code == 200
    assert post(a,ah,f'/v1/scheduling/meeting/{identifier}/confirm').status_code == 409
    assert b.put('/v1/availability',headers=bh,json={'status':'unknown'}).status_code == 200
    assert b.delete(f'/v1/friends/{friend}',headers=bh).status_code == 200
    assert post(a,ah,f'/v1/scheduling/meeting/{identifier}/confirm').status_code == 409
    assert a.get('/v1/calendar/events').json()['items'] == []


def test_group_needs_all_recipients_and_ai_rejection_has_no_effect(people,monkeypatch):
    a,b,c,ah,bh,ch,au,bu,friend,body = people
    cu=c.get('/v1/friends').json()['username']
    third=a.post('/v1/friends',headers=ah,json={'username':cu}).json()['id']
    c.post(f'/v1/friends/{third}/accept',headers=ch)
    identifier=post(a,ah,'/v1/scheduling/meeting',{**body,'friend_usernames':[bu,cu]}).json()['id']
    assert post(b,bh,f'/v1/scheduling/meeting/{identifier}/respond',{'accepted':True}).json()['status'] == 'pending'
    assert post(a,ah,f'/v1/scheduling/meeting/{identifier}/confirm').status_code == 409
    assert post(c,ch,f'/v1/scheduling/meeting/{identifier}/respond',{'accepted':True}).json()['status'] == 'ready_to_book'
    assert post(a,ah,f'/v1/scheduling/meeting/{identifier}/confirm').status_code == 200
    assert len(c.get('/v1/calendar/events').json()['items']) == 1
    monkeypatch.setattr(Planner,'parse',lambda *args,**kwargs: Intent(kind='scheduling',schedule_action='set_status',value='busy'))
    task,_=send(a,ah,'Set my profile busy')
    payload={key:task['action'][key] for key in ('decision_id','fingerprint','plan_revision')}
    payload['decision']='reject'
    assert post(a,ah,f"/v1/tasks/{task['id']}/decisions",payload).status_code == 202
    assert wait(a,task['id'])['reply']=='Nothing was sent or changed.'
    assert a.get('/v1/availability').json()['status']=='unknown'


def test_worker_lease_blocks_duplicates_and_recovers_approved_action(people,monkeypatch):
    from sixth.models import uid
    from sixth.runtime import Runtime
    from sixth.tasks import submit_message

    a,b,c,ah,bh,ch,au,bu,friend,body = people
    runtime=a.app.state.runtime
    owner=a.get('/v1/session').json()['account']
    task_id=submit_message(runtime.store,owner,uid(),'I am vegetarian')
    assert runtime.claim(owner,task_id)
    second=Runtime(runtime.store,runtime.memory,runtime.planner)
    try:
        assert not second.claim(owner,task_id)
        second.recover()
        assert runtime.store.get(owner,'task',task_id)['status']=='queued'
        runtime.renew(owner,task_id,release=True)
        second.recover()
        assert runtime.store.get(owner,'task',task_id)['status']=='completed'
        assert runtime.store.get(owner,'task_lease',task_id)['worker'] is None
        second.recover()
        assert len(runtime.memory.current(owner)) == 1
        # A lost worker may leave an already approved action awaiting execution.
        monkeypatch.setattr(Planner,'parse',lambda *args,**kwargs: Intent(kind='scheduling',schedule_action='add_event',meeting_title=body['title'],starts_at=body['starts_at'],ends_at=body['ends_at']))
        proposal={'id':submit_message(runtime.store,owner,uid(),'internal test')}
        runtime.run(owner,proposal['id'])
        pending=runtime.store.get(owner,'task',proposal['id'])
        pending.update(status='running',decision='approve')
        runtime.store.put(owner,'task',pending)
        runtime.store.put(owner,'task_lease',{'id':proposal['id'],'worker':'lost-worker','expires_at':'2020-01-01T00:00:00+00:00'})
        second.recover()
        assert runtime.store.get(owner,'task',proposal['id'])['status']=='completed'
        assert len(runtime.scheduling.own_events(owner))==1
        second.recover()
        assert len(runtime.scheduling.own_events(owner))==1
    finally:
        second.close()
