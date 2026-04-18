/**
 * Lazy Loading Component - Carregamento Preguiçoso de Dados
 * 
 * Otimiza performance carregando dados apenas quando necessário
 */
import React from 'react'
import { Loading } from '../components/Loading'

// lazyLoad, useInView e useInfiniteScroll: importar de @/utils/lazyLoadComponent e @/hooks/* (react-refresh).

// ==================== Intersection Observer para Lazy Loading ====================

interface LazyLoadProps {
  children: React.ReactNode;
  className?: string;
  threshold?: number;
  rootMargin?: string;
  placeholder?: React.ReactNode;
  onVisible?: () => void;
}

/**
 * Componente que carrega conteúdo apenas quando visível na tela
 */
export function LazyLoadContent({
  children,
  className = '',
  threshold = 0.1,
  rootMargin = '50px',
  placeholder,
  onVisible
}: LazyLoadProps) {
  const [isVisible, setIsVisible] = React.useState(false);
  const ref = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          onVisible?.();
          observer.disconnect();
        }
      },
      { threshold, rootMargin }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold, rootMargin, onVisible]);

  return (
    <div ref={ref} className={className}>
      {isVisible ? children : (placeholder || <div className="h-64 bg-gray-100 dark:bg-gray-800 animate-pulse rounded" />)}
    </div>
  );
}

// ==================== Lazy Image Loading ====================

interface LazyImageProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  src: string;
  alt: string;
  placeholder?: string;
  className?: string;
}

/**
 * Imagem com lazy loading nativo
 */
export function LazyImage({
  src,
  alt,
  placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%23ccc" width="400" height="300"/%3E%3C/svg%3E',
  className = '',
  ...props
}: LazyImageProps) {
  const [imgSrc, setImgSrc] = React.useState(placeholder);
  const [isLoaded, setIsLoaded] = React.useState(false);

  return (
    <img
      src={imgSrc}
      alt={alt}
      loading="lazy"
      onLoad={() => setIsLoaded(true)}
      onError={() => setImgSrc(placeholder)}
      className={`${className} ${isLoaded ? 'opacity-100' : 'opacity-50'} transition-opacity duration-300`}
      {...props}
      ref={(img) => {
        if (img && img.complete) {
          setImgSrc(src);
        }
      }}
    />
  );
}

// ==================== Infinite Scroll ====================

interface InfiniteScrollProps {
  children: React.ReactNode;
  hasMore: boolean;
  isLoading: boolean;
  onLoadMore: () => void;
  loader?: React.ReactNode;
  threshold?: number;
}

/**
 * Infinite scroll - carrega mais dados ao rolar até o fim
 */
export function InfiniteScroll({
  children,
  hasMore,
  isLoading,
  onLoadMore,
  loader,
  threshold = 0.8
}: InfiniteScrollProps) {
  const observerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (!hasMore || isLoading) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          onLoadMore();
        }
      },
      { threshold }
    );

    if (observerRef.current) {
      observer.observe(observerRef.current);
    }

    return () => observer.disconnect();
  }, [hasMore, isLoading, onLoadMore, threshold]);

  return (
    <>
      {children}
      
      {hasMore && (
        <div ref={observerRef} className="py-8">
          {isLoading && (loader || <Loading type="spinner" />)}
        </div>
      )}
      
      {!hasMore && !isLoading && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          ✅ Todos os itens foram carregados
        </div>
      )}
    </>
  );
}

// ==================== Virtual Scroll (para listas grandes) ====================

interface VirtualScrollProps<T> {
  items: T[];
  itemHeight: number;
  containerHeight: number;
  renderItem: (item: T, index: number) => React.ReactNode;
  overscan?: number;
}

/**
 * Virtual scroll - renderiza apenas itens visíveis
 * Para listas muito grandes (milhares de itens)
 */
export function VirtualScroll<T>({
  items,
  itemHeight,
  containerHeight,
  renderItem,
  overscan = 3
}: VirtualScrollProps<T>) {
  const [scrollTop, setScrollTop] = React.useState(0);

  const totalHeight = items.length * itemHeight;
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const endIndex = Math.min(
    items.length - 1,
    Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
  );

  const visibleItems = items.slice(startIndex, endIndex + 1);

  return (
    <div
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.currentTarget.scrollTop)}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div
          style={{
            transform: `translateY(${startIndex * itemHeight}px)`,
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0
          }}
        >
          {visibleItems.map((item, idx) => (
            <div
              key={startIndex + idx}
              style={{ height: itemHeight }}
            >
              {renderItem(item, startIndex + idx)}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ==================== Exemplo de Uso ====================

/**
 * Exemplo: Lista de investigações com infinite scroll
 */
/*
function InvestigationsList() {
  const fetchInvestigations = async (cursor?: string) => {
    const response = await api.get('/investigations', {
      params: { cursor, limit: 20 }
    });
    return response.data;
  };

  const { items, isLoading, hasMore, loadMore } = useInfiniteScroll(fetchInvestigations);

  return (
    <InfiniteScroll
      hasMore={hasMore}
      isLoading={isLoading}
      onLoadMore={loadMore}
    >
      {items.map((investigation) => (
        <LazyLoadContent key={investigation.id}>
          <InvestigationCard investigation={investigation} />
        </LazyLoadContent>
      ))}
    </InfiniteScroll>
  );
}
*/

/**
 * Exemplo: Lazy load de componente pesado
 */
/*
const HeavyChart = lazyLoad(() => import('./components/HeavyChart'));

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <HeavyChart data={data} />
    </div>
  );
}
*/
