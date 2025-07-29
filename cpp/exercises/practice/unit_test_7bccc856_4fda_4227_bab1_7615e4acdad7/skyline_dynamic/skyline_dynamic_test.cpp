#include "skyline_dynamic.h"
#include "catch.hpp"
#include <vector>
#include <utility>
#include <sstream>

TEST_CASE("Basic skyline operations") {
    skyline_dynamic::Skyline skyline;
    
    SECTION("Single building") {
        skyline.add(1, 5, 10);
        auto result = skyline.query();
        
        std::vector<std::pair<int, int>> expected = {
            {1, 10}, {5, 0}
        };
        
        REQUIRE(result == expected);
    }
    
    SECTION("Two non-overlapping buildings") {
        skyline.add(1, 5, 10);
        skyline.add(7, 12, 15);
        auto result = skyline.query();
        
        std::vector<std::pair<int, int>> expected = {
            {1, 10}, {5, 0}, {7, 15}, {12, 0}
        };
        
        REQUIRE(result == expected);
    }
    
    SECTION("Three buildings with overlap") {
        skyline.add(1, 5, 10);
        skyline.add(7, 12, 15);
        skyline.add(5, 7, 12);
        auto result = skyline.query();
        
        std::vector<std::pair<int, int>> expected = {
            {1, 10}, {5, 12}, {7, 15}, {12, 0}
        };
        
        REQUIRE(result == expected);
    }
    
    SECTION("Building with same height") {
        skyline.add(1, 5, 10);
        skyline.add(3, 8, 10);
        auto result = skyline.query();
        
        std::vector<std::pair<int, int>> expected = {
            {1, 10}, {8, 0}
        };
        
        REQUIRE(result == expected);
    }
    
    SECTION("Building completely covering another") {
        skyline.add(3, 7, 8);
        skyline.add(2, 9, 10);
        auto result = skyline.query();
        
        std::vector<std::pair<int, int>> expected = {
            {2, 10}, {9, 0}
        };
        
        REQUIRE(result == expected);
    }
    
    SECTION("Building nested inside another") {
        skyline.add(1, 10, 5);
        skyline.add(3, 7, 10);
        auto result = skyline.query();
        
        std::vector<std::pair<int, int>> expected = {
            {1, 5}, {3, 10}, {7, 5}, {10, 0}
        };
        
        REQUIRE(result == expected);
    }
}

TEST_CASE("Process commands") {
    skyline_dynamic::Skyline skyline;
    
    SECTION("Add command") {
        std::string result = skyline.process_command("add 1 5 10");
        REQUIRE(result.empty());
        
        auto skyline_result = skyline.query();
        std::vector<std::pair<int, int>> expected = {
            {1, 10}, {5, 0}
        };
        REQUIRE(skyline_result == expected);
    }
    
    SECTION("Query command") {
        skyline.process_command("add 1 5 10");
        skyline.process_command("add 7 12 15");
        
        std::string result = skyline.process_command("query");
        REQUIRE(result == "(1, 10) (5, 0) (7, 15) (12, 0)");
    }
    
    SECTION("Multiple buildings example") {
        skyline.process_command("add 1 5 10");
        skyline.process_command("add 7 12 15");
        std::string result1 = skyline.process_command("query");
        REQUIRE(result1 == "(1, 10) (5, 0) (7, 15) (12, 0)");
        
        skyline.process_command("add 5 7 12");
        std::string result2 = skyline.process_command("query");
        REQUIRE(result2 == "(1, 10) (5, 12) (7, 15) (12, 0)");
    }
}

TEST_CASE("Complex skyline scenarios") {
    skyline_dynamic::Skyline skyline;
    
    SECTION("Multiple overlapping buildings") {
        skyline.add(2, 9, 10);
        skyline.add(3, 7, 15);
        skyline.add(5, 12, 12);
        skyline.add(15, 20, 10);
        skyline.add(19, 24, 8);
        
        auto result = skyline.query();
        std::vector<std::pair<int, int>> expected = {
            {2, 10}, {3, 15}, {7, 12}, {12, 0}, 
            {15, 10}, {20, 8}, {24, 0}
        };
        
        REQUIRE(result == expected);
    }
    
    SECTION("Buildings with same start point") {
        skyline.add(1, 5, 10);
        skyline.add(1, 3, 15);
        skyline.add(1, 8, 8);
        
        auto result = skyline.query();
        std::vector<std::pair<int, int>> expected = {
            {1, 15}, {3, 10}, {5, 8}, {8, 0}
        };
        
        REQUIRE(result == expected);
    }
    
    SECTION("Buildings with same end point") {
        skyline.add(1, 10, 10);
        skyline.add(3, 10, 15);
        skyline.add(7, 10, 8);
        
        auto result = skyline.query();
        std::vector<std::pair<int, int>> expected = {
            {1, 10}, {3, 15}, {10, 0}
        };
        
        REQUIRE(result == expected);
    }
}

TEST_CASE("Edge cases") {
    skyline_dynamic::Skyline skyline;
    
    SECTION("Adjacent buildings") {
        skyline.add(1, 5, 10);
        skyline.add(5, 10, 15);
        
        auto result = skyline.query();
        std::vector<std::pair<int, int>> expected = {
            {1, 10}, {5, 15}, {10, 0}
        };
        
        REQUIRE(result == expected);
    }
    
    SECTION("Multiple buildings with same height") {
        skyline.add(1, 5, 10);
        skyline.add(7, 12, 10);
        skyline.add(14, 20, 10);
        
        auto result = skyline.query();
        std::vector<std::pair<int, int>> expected = {
            {1, 10}, {5, 0}, {7, 10}, {12, 0}, {14, 10}, {20, 0}
        };
        
        REQUIRE(result == expected);
    }
    
    SECTION("Large coordinate values") {
        skyline.add(1000000000, 1000000005, 10);
        skyline.add(1000000002, 1000000007, 15);
        
        auto result = skyline.query();
        std::vector<std::pair<int, int>> expected = {
            {1000000000, 10}, {1000000002, 15}, {1000000007, 0}
        };
        
        REQUIRE(result == expected);
    }
}