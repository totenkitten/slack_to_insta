# slack_to_insta
Script that gets all your old images out of Slack and puts them on Instagram.

This was originally written to take all the images posted on the Totenkitten internal Slack and post them to Instagram, and then remove them from Slack to free up space. 

The plan was kiboshed because people didn't want pictures of themselves on Instagram, and because it would leak Imperial planning information to the unwashed masses, who are mentally ill-prepared and prone to fantods. As a result, the part where it uses the inital comment on the Slack image as the IG caption isn't really tested, and so might throw KeyError exceptions or something. 

If you want to use it on your own Slack, you'll need to update the file passwords.py with your own information, you can't have ours. 
