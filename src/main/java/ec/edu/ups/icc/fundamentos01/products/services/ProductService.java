package ec.edu.ups.icc.fundamentos01.products.services;

import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Slice;
import ec.edu.ups.icc.fundamentos01.products.dtos.CreateProductDto;
import ec.edu.ups.icc.fundamentos01.products.dtos.UpdateProductDto;
import ec.edu.ups.icc.fundamentos01.products.dtos.ProductResponseDto;

public interface ProductService {

    ProductResponseDto create(CreateProductDto dto);

    // Renombramos findAllPaginado a findAll para seguir el estándar de la guía
    Page<ProductResponseDto> findAll(int page, int size, String[] sort);

    Slice<ProductResponseDto> findAllSlice(int page, int size, String[] sort);

    List<ProductResponseDto> findAllList(); // Tu antiguo findAll (sin paginación)

    ProductResponseDto findById(Long id);

    // Versión paginada del buscador
    Page<ProductResponseDto> findWithFilters(
            String name, Double minPrice, Double maxPrice, Long categoryId,
            int page, int size, String[] sort);

    // Versión paginada de productos por usuario
    Page<ProductResponseDto> findByUserIdWithFilters(
            Long userId, String name, Double minPrice, Double maxPrice, Long categoryId,
            int page, int size, String[] sort);

    // Métodos legacy (listas simples)
    List<ProductResponseDto> findByUserId(Long id);

    List<ProductResponseDto> findByCategoryId(Long id);

    ProductResponseDto update(Long id, UpdateProductDto dto);

    void delete(Long id);
}