def test_health(client): assert client.get('/health').json()['status']=='healthy'
def test_machine_retrieval(client):
    data=client.get('/api/machines').json(); assert len(data)>=4 and data[0]['name']=='CNC Machine 01'
def test_normal_reading(client):
    r=client.post('/api/simulator/machines/1/reading',json={'machine_id':1,'temperature':55,'vibration':2,'pressure':55}); assert r.status_code==200
def test_abnormal_detection_and_score(client):
    client.post('/api/simulator/readings',json={'machine_id':2,'scenario':'high_vibration'})
    m=client.get('/api/machines/2').json(); assert m['status']=='Critical' and m['health_score']<60
def test_sensor_failure_and_alert(client):
    r=client.post('/api/simulator/machines/3/failure/temperature'); assert r.status_code==200
    assert client.get('/api/machines/3').json()['status']=='Sensor Failure'
    alerts=client.get('/api/alerts').json(); assert any(a['alert_type']=='Sensor Failure' and a['machine_id']==3 for a in alerts)
def test_restore_and_risk(client):
    client.post('/api/simulator/machines/3/restore/temperature'); m=client.get('/api/machines/3').json(); assert m['status']=='Healthy' and m['risk_level']=='Low'
def test_errors(client):
    assert client.get('/api/machines/999').status_code==404
    assert client.post('/api/simulator/machines/1/failure/nope').status_code==422
