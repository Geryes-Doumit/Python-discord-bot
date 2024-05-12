import datetime
import json
from dateutil import tz
import os.path
import discord
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


def profedt(name, jours)->discord.Embed:
  creds = None
  if os.path.exists("googleapi/token.json"):
    creds = Credentials.from_authorized_user_file("googleapi/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "googleapi/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("googleapi/token.json", "w") as token:
      token.write(creds.to_json())
      
  embed = discord.Embed(title="Emploi du temps de '" + name + "'", color=discord.Color.blurple())
  
  try:
    service = build("calendar", "v3", credentials=creds)
    calendar_id = json.load(open("googleapi/calendar_id.json"))["id"]

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    morning = datetime.datetime.utcnow()
    morning = morning.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    week = datetime.datetime.utcnow() + datetime.timedelta(days=jours)
    week = week.replace(hour=23, minute=0, second=0, microsecond=0).isoformat() + "Z"
    nevents = 100
    print("Getting the events of " + name +" for the next week")
    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=morning,
            timeMax=week,
            maxResults=nevents,
            singleEvents=True,
            orderBy="startTime",
            q=name.upper() or name.lower() or name.capitalize() or name.title() or name,
        )
        .execute()
    )
    events = events_result.get("items", [])

    if not events:
      return embed.add_field(name="Oups...", value="Aucun évènement trouvé")

    cut_early = False
    # Prints the start and name of the next 10 events
    for event in events:
        if len(embed) > 5800:
          cut_early = True
          break
        start_string = (event["start"].get("dateTime"))
        end_string = (event["end"].get("dateTime"))
        start_date_object = datetime.datetime.strptime(start_string, "%Y-%m-%dT%H:%M:%SZ")
        start_date_object = start_date_object.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
        end_date_object = datetime.datetime.strptime(end_string, "%Y-%m-%dT%H:%M:%SZ")
        end_date_object = end_date_object.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
        
        date_to_show = days[start_date_object.weekday()] + " " + str(start_date_object.day) + " " + months[start_date_object.month-1]
        
        event_name = str(event['summary']).strip()
        event_duration = "de " + str(start_date_object.time().strftime("%Hh%M")) + \
                         " à " + str(end_date_object.time().strftime("%Hh%M"))
        location = 'Salle : ' + str(event['location']).strip() 
        description = str(event['description']).strip()
        description = re.sub(r'\(Exporté.*[0-9]\)\n?', '', description)
        
        embed_desc = "> " + event_name + ", " + event_duration + "\n> " \
                + location + "\n> " \
                + description.replace("\n", ", ").removesuffix(', ') + "\n"
                
        if len(embed_desc) > 4096:
          # consider the 4093 first characters and add "..." at the end
          embed_desc = embed_desc[:4093] + "..."
        
        try:
          if embed.fields[-1].name is not None and date_to_show in embed.fields[-1].name:
              embed.set_field_at(-1, name=date_to_show, value=embed.fields[-1].value + "\n" + embed_desc, inline=False) # type: ignore
          else:
            if len(embed.fields) < 25:
              embed.add_field(name=date_to_show, value=embed_desc, inline=False)
        except:
            if len(embed.fields) < 25:
              embed.add_field(name=date_to_show, value=embed_desc, inline=False)
        
    cut_early_string = "(coupé à 5800 caractères)" if cut_early else ""
    embed.set_footer(text="Emploi du temps des " + str(jours) + " prochains jours. " + cut_early_string
                     + "\nCritère de recherche: '" + name + "' · le " + datetime.datetime.now().strftime("%d/%m/%Y à %H:%M"))
    
    return embed

  except HttpError as error:
    return embed.add_field(name="Erreur", value=f"Une erreur est survenue: {error}")