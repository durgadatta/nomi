from tools.parser_spikes.parse_matrix import MatrixRow, render_matrix


def test_parse_matrix_renders_frontend_roles():
    output = render_matrix(
        [
            MatrixRow(
                frontend="example",
                roles="fast, readable",
                fixture="demo.nomi",
                status="pass",
                milliseconds=1.25,
            )
        ]
    )

    assert "| frontend | roles | fixture | status | ms | error |" in output
    assert "| example | fast, readable | demo.nomi | pass | 1.250 |  |" in output
