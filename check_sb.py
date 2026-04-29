import urllib.request
url = 'https://dnbsgjmscuycjwrnknyj.supabase.co/rest/v1/fileevent?select=*&order=timestamp.desc&limit=5'
req = urllib.request.Request(url, headers={'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRuYnNnam1zY3V5Y2p3cm5rbnlqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1MTY5MDYsImV4cCI6MjA5MjA5MjkwNn0.M9bQLJRlbEzFQb39q3r8gTbktgMdOTlxX9nw9cy5NxU'})
with urllib.request.urlopen(req) as r:
    print(r.read().decode())
