from managers.database import DatabaseManager


def main():

    print(
        "================================"
    )

    print(
        "space_shooter TEST"
    )

    print(
        "================================"
    )


    db = DatabaseManager()


    # Initialize database

    print(
        "\nCreating database and tables..."
    )

    db.initialize_database()


    # --------------------------------
    # TEST INSERT
    # --------------------------------

    print(
        "\nTesting INSERT..."
    )

    test_id = db.test_insert()

    print(
        "INSERT successful!"
    )

    print(
        "Temporary Player ID:",
        test_id
    )


    # --------------------------------
    # CREATE PLAYER
    # --------------------------------

    print(
        "\nRegistering player..."
    )

    player_id = db.register_player(
        "DemoPlayer",
        "demo@example.com"
    )

    print(
        "Player registered!"
    )

    print(
        "Player ID:",
        player_id
    )


    # --------------------------------
    # READ PLAYER
    # --------------------------------

    print(
        "\nReading player..."
    )

    player = db.get_player(
        player_id=player_id
    )

    print(
        player
    )


    # --------------------------------
    # SAVE SCORE
    # --------------------------------

    print(
        "\nSaving scores..."
    )

    db.save_score(
        player_id,
        100
    )

    db.save_score(
        player_id,
        250
    )

    db.save_score(
        player_id,
        500
    )


    print(
        "Scores saved!"
    )


    # --------------------------------
    # LEADERBOARD
    # --------------------------------

    print(
        "\nLeaderboard:"
    )

    leaderboard = db.get_leaderboard()


    for index, player in enumerate(
        leaderboard,
        start=1
    ):

        print(
            f"{index}. "
            f"{player['username']} - "
            f"{player['best_score']}"
        )


    # --------------------------------
    # UPDATE PLAYER
    # --------------------------------

    print(
        "\nUpdating player profile..."
    )

    db.update_player(
        player_id,
        username="DemoPlayerUpdated",
        email="updated@example.com"
    )


    updated_player = db.get_player(
        player_id=player_id
    )


    print(
        "Updated player:"
    )

    print(
        updated_player
    )


    # --------------------------------
    # SCORE HISTORY
    # --------------------------------

    print(
        "\nScore history:"
    )

    scores = db.get_player_scores(
        player_id
    )


    for score in scores:

        print(
            score
        )


    # --------------------------------
    # DELETE PLAYER
    # --------------------------------

    print(
        "\nDeleting test player..."
    )

    db.delete_player(
        player_id
    )


    print(
        "Player deleted."
    )


    print(
        "\n================================"
    )

    print(
        "ALL DATABASE TESTS COMPLETE"
    )

    print(
        "================================"
    )


if __name__ == "__main__":

    main()