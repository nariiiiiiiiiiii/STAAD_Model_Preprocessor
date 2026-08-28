#include <iostream>
#include <string_view>

#include "neutral_contract.h"

namespace {

bool has_arg(int argc, char** argv, std::string_view expected) {
    for (int index = 1; index < argc; ++index) {
        if (std::string_view(argv[index]) == expected) {
            return true;
        }
    }
    return false;
}

void print_capabilities() {
    std::cout
        << "{\"protocol_version\":"
        << staadprep::skp_reader::kNeutralProtocolVersion
        << ",\"sketchup_sdk\":false,\"reader_ready\":false,"
        << "\"message\":\"SKP importer unavailable - DXF remains available\"}"
        << std::endl;
}

}  // namespace

int main(int argc, char** argv) {
    if (has_arg(argc, argv, "--capabilities")) {
        print_capabilities();
        return 0;
    }

    std::cerr
        << "Native SKP edge extraction is not linked yet. "
        << "Stage the official SketchUp SDK under vendor/sketchup-sdk/ "
        << "and complete Task 15."
        << std::endl;
    return 2;
}
