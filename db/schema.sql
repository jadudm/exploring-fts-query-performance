SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: raw_content; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.raw_content (
    id bigint NOT NULL,
    domain64 bigint NOT NULL,
    path text NOT NULL,
    tag text DEFAULT 'p'::text NOT NULL,
    content text NOT NULL
);


--
-- Name: raw_content_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.raw_content ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.raw_content_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(128) NOT NULL
);


--
-- Name: searchable_content; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.searchable_content (
    rowid bigint NOT NULL,
    domain64 bigint NOT NULL,
    path text NOT NULL,
    tag text DEFAULT 'p'::text NOT NULL,
    content text NOT NULL,
    fts tsvector GENERATED ALWAYS AS (to_tsvector('english'::regconfig, content)) STORED
);


--
-- Name: searchable_content_rowid_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.searchable_content ALTER COLUMN rowid ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.searchable_content_rowid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: raw_content raw_content_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.raw_content
    ADD CONSTRAINT raw_content_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: searchable_content searchable_content_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.searchable_content
    ADD CONSTRAINT searchable_content_pkey PRIMARY KEY (rowid);


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20250111191511');
