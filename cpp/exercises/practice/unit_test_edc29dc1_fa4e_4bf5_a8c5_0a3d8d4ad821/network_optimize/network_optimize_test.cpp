#include "network_optimize.h"
#include "catch.hpp"
#include <sstream>
#include <string>

TEST_CASE("Basic routing success") {
    std::istringstream input(
        "add_link 0 1 1000 1\n"
        "add_link 1 2 500 2\n"
        "route 0 2 1500 10\n"
    );
    std::ostringstream output;
    network_optimize::processCommands(input, output);
    std::string expected = 
        "2\n"
        "0 1 2\n"
        "0 1 2\n";
    CHECK(output.str() == expected);
}

TEST_CASE("Routing fails due to deadline") {
    std::istringstream input(
        "add_link 0 1 1000 1\n"
        "route 0 2 1500 5\n"
    );
    std::ostringstream output;
    network_optimize::processCommands(input, output);
    std::string expected = "ERROR: Deadline cannot be met.\n";
    CHECK(output.str() == expected);
}

TEST_CASE("Link failure handling") {
    std::istringstream input(
        "add_link 0 1 1000 1\n"
        "add_link 1 2 500 2\n"
        "route 0 2 1500 10\n"
        "link_failure 1 2\n"
        "route 0 2 1500 10\n"
    );
    std::ostringstream output;
    network_optimize::processCommands(input, output);
    std::string expected = 
        "2\n"
        "0 1 2\n"
        "0 1 2\n"
        "ERROR: Deadline cannot be met.\n";
    CHECK(output.str() == expected);
}

TEST_CASE("Bandwidth update improves routing") {
    std::istringstream input(
        "add_link 0 1 1000 1\n"
        "add_link 1 2 500 2\n"
        "route 0 2 2000 10\n"
        "update_bandwidth 1 2 1000\n"
        "route 0 2 2000 10\n"
    );
    std::ostringstream output;
    network_optimize::processCommands(input, output);
    std::string expected = 
        "ERROR: Deadline cannot be met.\n"
        "2\n"
        "0 1 2\n"
        "0 1 2\n";
    CHECK(output.str() == expected);
}