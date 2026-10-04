import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QInputDialog,
    QListWidgetItem
)


class FantasyCricketApp(QMainWindow):

    def __init__(self):
        super().__init__()

        # Load UI
        uic.loadUi("fantasy_cricket.ui", self)

        self.setWindowTitle("Fantasy Cricket League")

        # Team settings
        self.total_points = 1000
        self.used_points = 0
        self.selected_players = []
        self.team_name = ""

        # Database connection
        self.db = sqlite3.connect("cricket.db")
        self.cur = self.db.cursor()

        # Connect UI signals
        self.categoryCombo.currentTextChanged.connect(self.load_players)
        self.availableList.itemDoubleClicked.connect(self.add_player)
        self.selectedList.itemDoubleClicked.connect(self.remove_player)

        # Initial labels
        self.labelAvailable.setText(
            f"Points Available: {self.total_points}"
        )
        self.labelUsed.setText(
            f"Points Used: {self.used_points}"
        )

        # Menu actions
        self.menuBar().addAction("New Team").triggered.connect(
            self.new_team
        )

        self.menuBar().addAction("Save Team").triggered.connect(
            self.save_team
        )

        self.menuBar().addAction("Evaluate Team").triggered.connect(
            self.evaluate_team
        )

        # Load initial players
        self.load_players()

    # ---------------------------------------------------------
    # LOAD PLAYERS
    # ---------------------------------------------------------

    def load_players(self):
        category = self.categoryCombo.currentText()

        self.availableList.clear()

        self.cur.execute(
            "SELECT player FROM stats WHERE ctg = ?",
            (category,)
        )

        players = self.cur.fetchall()

        for player in players:
            player_name = player[0]

            # Don't show already selected players
            if player_name not in self.selected_players:
                self.availableList.addItem(player_name)

    # ---------------------------------------------------------
    # NEW TEAM
    # ---------------------------------------------------------

    def new_team(self):

        team_name, ok = QInputDialog.getText(
            self,
            "New Team",
            "Enter team name:"
        )

        if ok and team_name:

            self.team_name = team_name

            self.selected_players.clear()
            self.selectedList.clear()

            self.used_points = 0

            self.labelUsed.setText("Points Used: 0")
            self.labelAvailable.setText(
                f"Points Available: {self.total_points}"
            )

            self.load_players()

    # ---------------------------------------------------------
    # ADD PLAYER
    # ---------------------------------------------------------

    def add_player(self, item):

        player = item.text()

        # Prevent duplicate players
        if player in self.selected_players:
            return

        # Maximum 11 players
        if len(self.selected_players) >= 11:

            QMessageBox.warning(
                self,
                "Limit Reached",
                "You can only select 11 players."
            )

            return

        # Get player value
        self.cur.execute(
            "SELECT value FROM stats WHERE player = ?",
            (player,)
        )

        value = self.cur.fetchone()

        if value:

            value = value[0]

            # Check points
            if self.used_points + value > self.total_points:

                QMessageBox.warning(
                    self,
                    "Points Exceeded",
                    "Not enough points available."
                )

                return

            # Add player
            self.used_points += value
            self.selected_players.append(player)

            self.selectedList.addItem(
                QListWidgetItem(player)
            )

            # Update points
            self.labelUsed.setText(
                f"Points Used: {self.used_points}"
            )

            self.labelAvailable.setText(
                f"Points Available: "
                f"{self.total_points - self.used_points}"
            )

            # Refresh available players
            self.load_players()

    # ---------------------------------------------------------
    # REMOVE PLAYER
    # ---------------------------------------------------------

    def remove_player(self, item):

        player = item.text()

        self.cur.execute(
            "SELECT value FROM stats WHERE player = ?",
            (player,)
        )

        value = self.cur.fetchone()

        if value:

            self.used_points -= value[0]

            if player in self.selected_players:
                self.selected_players.remove(player)

            self.selectedList.takeItem(
                self.selectedList.row(item)
            )

            # Update points
            self.labelUsed.setText(
                f"Points Used: {self.used_points}"
            )

            self.labelAvailable.setText(
                f"Points Available: "
                f"{self.total_points - self.used_points}"
            )

            # Refresh available players
            self.load_players()

    # ---------------------------------------------------------
    # SAVE TEAM
    # ---------------------------------------------------------

    def save_team(self):

        if not self.team_name:

            QMessageBox.warning(
                self,
                "Error",
                "Please create a team first."
            )

            return

        if not self.selected_players:

            QMessageBox.warning(
                self,
                "Error",
                "No players selected."
            )

            return

        players_str = ",".join(self.selected_players)

        self.cur.execute(
            """
            INSERT OR REPLACE INTO teams
            (name, players, value)
            VALUES (?, ?, ?)
            """,
            (
                self.team_name,
                players_str,
                self.used_points
            )
        )

        self.db.commit()

        QMessageBox.information(
            self,
            "Saved",
            "Team saved successfully!"
        )

    # ---------------------------------------------------------
    # CALCULATE PLAYER FANTASY POINTS
    # ---------------------------------------------------------

    def calculate_player_points(self, player):

        self.cur.execute(
            """
            SELECT scored, faced, four, sixes,
                   bowled, maiden, given, wkts,
                   catches, stumping, ro
            FROM match
            WHERE player = ?
            """,
            (player,)
        )

        data = self.cur.fetchone()

        if not data:
            return 0

        (
            scored,
            faced,
            four,
            sixes,
            bowled,
            maiden,
            given,
            wkts,
            catches,
            stumping,
            ro
        ) = data

        points = 0

        # -------------------------
        # Batting points
        # -------------------------

        points += scored

        # 1 point per four
        points += four * 1

        # 2 points per six
        points += sixes * 2

        # Milestone bonus
        if scored >= 100:
            points += 16

        elif scored >= 50:
            points += 8

        # -------------------------
        # Bowling points
        # -------------------------

        points += wkts * 25

        points += maiden * 8

        # -------------------------
        # Fielding points
        # -------------------------

        points += catches * 8

        points += stumping * 12

        points += ro * 6

        # -------------------------
        # Economy bonus/penalty
        # -------------------------

        if bowled > 0:

            economy = given / bowled

            if economy < 5:
                points += 6

            elif economy < 7:
                points += 4

            elif economy > 10:
                points -= 2

        return points

    # ---------------------------------------------------------
    # EVALUATE TEAM
    # ---------------------------------------------------------

    def evaluate_team(self):

        # Team name check
        if not self.team_name:

            QMessageBox.warning(
                self,
                "No Team",
                "Please create a team first."
            )

            return

        # Check number of players
        if len(self.selected_players) != 11:

            QMessageBox.warning(
                self,
                "Incomplete Team",
                "Please select exactly 11 players "
                "before evaluating the team."
            )

            return

        # Calculate total points
        total_fantasy_points = 0

        result_text = ""

        result_text += "FANTASY TEAM EVALUATION\n"
        result_text += "==============================\n\n"

        result_text += f"Team Name: {self.team_name}\n"
        result_text += f"Players: {len(self.selected_players)}\n"
        result_text += f"Points Used: {self.used_points}/1000\n\n"

        result_text += "PLAYER PERFORMANCE\n"
        result_text += "------------------------------\n"

        # Calculate each player
        for player in self.selected_players:

            fantasy_points = self.calculate_player_points(
                player
            )

            total_fantasy_points += fantasy_points

            result_text += (
                f"{player}: "
                f"{fantasy_points} fantasy points\n"
            )

        # Team rating
        if total_fantasy_points >= 300:
            rating = "Excellent"

        elif total_fantasy_points >= 200:
            rating = "Very Good"

        elif total_fantasy_points >= 100:
            rating = "Good"

        else:
            rating = "Needs Improvement"

        result_text += "\n"
        result_text += "==============================\n"
        result_text += (
            f"TOTAL FANTASY POINTS: "
            f"{total_fantasy_points}\n"
        )
        result_text += f"TEAM RATING: {rating}\n"
        result_text += "=============================="

        # Show evaluation in PyQt window
        QMessageBox.information(
            self,
            "Team Evaluation",
            result_text
        )

    # ---------------------------------------------------------
    # CLOSE DATABASE
    # ---------------------------------------------------------

    def closeEvent(self, event):

        self.db.close()

        event.accept()


# -------------------------------------------------------------
# MAIN PROGRAM
# -------------------------------------------------------------

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = FantasyCricketApp()

    window.show()

    sys.exit(app.exec_())

