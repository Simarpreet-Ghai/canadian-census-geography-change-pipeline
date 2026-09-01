from app.clean import build_staging_mappings
from app.compare import compare_id_matching
from app.ingest import load_raw_correspondence
from app.mapping import build_mapping_results
from app.validate import validate_mapping_results, validate_staging


def run_pipeline():
    print("Starting census geography pipeline...\n")

    print("1. Loading raw correspondence data")
    load_raw_correspondence()

    print("\n2. Building Ontario staging mappings")
    build_staging_mappings()

    print("\n3. Building geography mapping results")
    build_mapping_results()

    print("\n4. Validating staging data")
    validate_staging()

    print("\n5. Validating mapping results")
    validate_mapping_results()

    print("\n6. Comparing simple ID matching")
    compare_id_matching()

    print("\nPipeline completed.")


if __name__ == "__main__":
    run_pipeline()