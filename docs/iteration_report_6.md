# Mango Team Iteration 6

### Authors: Megan Dolan, Sargon Odicho, Jemima Egwurube, Naing Tun

|   | Name            | Email            | Telephone/Other Contact Info  |
|:---| :------------: | :--------------: | :----------: |
| 1 | Sargon Odicho   | sodicho@iwu.edu  | 847-877-1231 |
| 2 | Jemima Egwurube | jegwurub@iwu.edu | 309-532-5275 |
| 3 | Megan Dolan     | mdolan1@iwu.edu  | 309-706-5796 |
| 4 | Naing Tun 	  | ntun@iwu.edu	 | 309-684-8835 |

## Accomplishments this week:


What each person was responsible for accomplishing.

  + Naing = Added test cases for creating and login account. Fixed all the existing test cases that are failing (because they wouldn't work until the user create account and login into them. For instance, the user cannot add an entry without logging into their account)

  + Sargon = Added a "Show less" feature for long descriptions of assignments (still need to work on "Show More" and toggling between "Show more" and "Show less")
  
  + Megan = Added calender; updated styles of login/logout button

  + Jemima = Added timezone

What was completed.

+ Added/updated test cases for `login`, `logout`, `add_entry`, `edit_entry`, `delete_entry`

+ Made the description field look much nicer by truncating long descriptions
 
+ Updated the buttons of login/logout

+ Redirect the directories such as `./add` back to the login page if the user hasn't login yet. 

What troubles/issues/roadblocks/difficulties you encountered.

+ We are still working on calendar integration. We are also figuring out how to integrate too, in a sense that it would be more accessible (whether to display the assignments due on the selected date or just display the titles of assignment when the user hovers on the date, which Moodle does)

+ We are also working on "Show More/Less" button for description field

+ The test cases were a bit tricky because we restricted the user to not have certain funcionalities (such as add assignments) without logging into their account. In order to login, they have to create account first too. So, there are so many dependencies for each test case (`add_entry` would require the user to `create` and `login` account first)

One tool or process or approach you used that you felt was especially helpful, and why.

+ Meeting up before merging individual branches to the master was indeed helpful. It enabled us to explain our branch/code to each other.

What was planned but not finished.
+ "Show More/Less" button mentioned above

What adjustments to your overall design you discovered.

+ We need to fix the homepage (not `./homepage`, but the actual homepage `http://127.0.0.1:5000/`). We also need to tidy up our directory paths.

One important thing you learned during this iteration.

+ We learned how to format calendar in python and then transfer to HTML (which we thought was cool).

## Plan for Following Iteration (Week 7):

Which user stories and tasks you plan to complete in the coming iteration and in the two iterations following it.

+ Calendar integration (we have only added the calendar so far)

+ "Show More/Less" button

+ Update/add/clean CSS/UI Styling

+ More unit tests as we add more features

+ Color change when past due.

+ Optional: Alert/reminder.


Who will be responsible for each user story planned for the next iteration, not the following two.

+ The following will be individual work(s) assigned to each team member:

  + Naing = More test cases, helping with Calendar integration (and possibly "Show less/more" if Sargon needs help with Javascript/Jqeury)

  + Sargon = "Show less/more" button
  
  + Megan = Calendar integration, CSS styling

  + Jemima = CSS Styling, reminder system (if time permits)