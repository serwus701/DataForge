from typing import List
import logging

from fastapi import HTTPException
from src.utils.enums.generators import Generators
from src.services.iban.iban_generator import iban_generator
from src.services.person.person_generator import person_generator
from starlette import status

from src.services.base_generator import BaseGenerator

logger = logging.getLogger("DataGeneratorService")

generators: dict[BaseGenerator, list[str]] = {iban_generator: [], person_generator: []}


def get_available_generators_list() -> List[str]:
    return [enum.name.lower() for enum in Generators]


def generate_data(request_types: list[str]):
    if request_types is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Generators list cannot be empty!"
        )
    gen_types = []
    for generator in generators.keys():
        supported_datatypes = generator.get_supported_types()
        if not request_types:
            continue

        for sup_type in supported_datatypes:
            if sup_type in request_types:
                request_types.remove(sup_type)
                gen_types.append(sup_type)
        if gen_types:
            generators[generator] = gen_types
            gen_types = []
        print(f"Request types after generator: {request_types}")

    if request_types:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No generators for types: {request_types}"
        )
    response = {}
    for generator, datatypes in generators.items():
        if datatypes:
            response.update(generator.generate(datatypes))
        generators[generator] = []

    return response